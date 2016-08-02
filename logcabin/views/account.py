import requests

from pyramid.httpexceptions import HTTPBadRequest, HTTPFound, HTTPNotFound
from pyramid.renderers import render_to_response
from pyramid.security import forget, remember, NO_PERMISSION_REQUIRED
from pyramid.view import view_config
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message as EmailMessage
from requests.exceptions import RequestException
from requests_oauthlib import OAuth1Session
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound
from uuid import uuid4

from logcabin.lib.cherubplay import CherubplayClient
from logcabin.lib.msparp import MSPARPClient
from logcabin.models import User, TumblrAccount


def error_response(request, message):
    if request.is_xhr:
        return {"error": message}
    request.session.flash(message)
    return HTTPFound(request.headers.get("Referer") or request.route_path("home"))


def success_response(request, message):
    request.session.flash(message)
    go_to_url = request.headers.get("Referer") or request.route_path("home")
    if request.is_xhr:
        return {"go_to_url": go_to_url}
    return HTTPFound(go_to_url)


def send_email(request, action, user, email_address):
    email_token = str(uuid4())
    request.session.redis.setex(":".join([action, str(user.id), email_address]), 86400 if action == "verify" else 600, email_token)

    mailer = get_mailer(request)
    message = EmailMessage(
        subject=action.capitalize() + " your email address",
        sender="admin@logcabin.com",
        recipients=[email_address],
        body=request.route_url("account." + ("verify_email" if action == "verify" else "reset_password"), _query={
            "user_id": user.id, "email_address": email_address, "token": email_token,
        }),
    )
    mailer.send(message)


@view_config(route_name="account.register", request_method="POST", renderer="json", permission=NO_PERMISSION_REQUIRED)
def register(request):
    if (
        not request.POST.get("username")
        or not request.POST.get("email_address")
        or not request.POST.get("password")
        or not request.POST.get("password_again")
    ):
        return error_response(request, "Please fill in all the fields.")

    if request.POST["password"] != request.POST["password_again"]:
        return error_response(request, "Those passwords didn't match.")

    username = request.POST["username"].strip()[:User.username.type.length]
    if not User.username.type.regex.match(username):
        return error_response(request, "Usernames can only contain letters, numbers, hyphens and underscores.")

    email_address = request.POST["email_address"].strip()[:User.email_address.type.length]
    if not User.email_address.type.regex.match(email_address):
        return error_response(request, "Please enter a valid email address.")

    if (
        request.db.query(func.count("*")).select_from(User)
        .filter(func.lower(User.username) == username.lower()).scalar()
    ):
        return error_response(request, "There's already an account called %s. Please choose a different username." % username)

    if (
        request.db.query(func.count("*")).select_from(User)
        .filter(func.lower(User.email_address) == email_address.lower()).scalar()
    ):
        return error_response(request, "There's already an account with that email address.")

    new_user = User(
        username=username,
        email_address=email_address,
        email_verified=False,
        last_ip=request.remote_addr,
        # todo timezone?
    )
    new_user.set_password(request.POST["password"])
    request.db.add(new_user)
    request.db.flush()

    send_email(request, "verify", new_user, email_address)

    remember(request, new_user.id)
    return success_response(request, "Welcome to Log Cabin!")


@view_config(route_name="account.log_in", request_method="POST", renderer="json", permission=NO_PERMISSION_REQUIRED)
def log_in(request):
    if not request.POST.get("username") or not request.POST.get("password"):
        return error_response(request, "Please fill in all the fields.")

    try:
        username = request.POST["username"].strip()[:User.username.type.length]
        user = request.db.query(User).filter(func.lower(User.username) == username.lower()).one()
    except NoResultFound:
        return error_response(request, "There isn't an account called %s." % username)

    if user.check_password(request.POST["password"]):
        remember(request, user.id)
        return success_response(request, "Welcome to Log Cabin!")

    return error_response(request, "That's the wrong password.")


@view_config(route_name="account.log_out", request_method="POST")
def log_out(request):
    forget(request)
    request.session.flash("we'll miss u :'(")
    return HTTPFound(request.route_path("home"))


@view_config(route_name="account.forgot_password", request_method="GET", permission=NO_PERMISSION_REQUIRED, renderer="account/forgot_password.mako")
def forgot_password_get(request):
    return {}


@view_config(route_name="account.forgot_password", request_method="POST", permission=NO_PERMISSION_REQUIRED, renderer="base_unauthenticated.mako")
def forgot_password_post(request):
    try:
        username = request.POST["username"].strip()[:User.username.type.length]
        user = request.db.query(User).filter(func.lower(User.username) == username.lower()).one()
    except NoResultFound:
        request.session.flash("There isn't an account called %s." % username)
        return render_to_response("account/forgot_password.mako", {}, request)

    send_email(request, "reset", user, user.email_address)

    request.session.flash("We've sent a link to the email address on your account. Please check your email to finish resetting your password.")
    return {}


@view_config(route_name="account.verify_email", request_method="GET", permission=NO_PERMISSION_REQUIRED)
def verify_email(request):
    try:
        user_id = int(request.GET["user_id"].strip())
        email_address = request.GET["email_address"].strip()
        token = request.GET["token"].strip()
    except (KeyError, ValueError):
        raise HTTPNotFound
    stored_token = request.session.redis.get("verify:%s:%s" % (user_id, email_address))
    if not user_id or not email_address or not token or not stored_token:
        raise HTTPNotFound

    stored_token = stored_token.decode("utf-8")

    if not stored_token == token:
        raise HTTPNotFound

    if (
        request.db.query(func.count("*")).select_from(User)
        .filter(func.lower(User.email_address) == email_address.lower()).scalar()
    ):
        request.session.flash("There's already an account with that email address.")
        return HTTPFound(request.route_path("home"))

    try:
        user = request.db.query(User).filter(User.id == user_id).one()
    except NoResultFound:
        raise HTTPNotFound

    user.email_address = email_address
    user.email_verified = True

    remember(request, user.id)
    request.session.flash("Your email address has been verified.")

    return HTTPFound(request.route_path("home"))


@view_config(route_name="account.settings", request_method="GET", renderer="account/settings.mako")
def settings(request):
    cherubplay_accounts = []
    msparp_accounts = []
    if request.user.email_verified:
        try:
            if "urls.cherubplay" in request.registry.settings:
                cherubplay_accounts = CherubplayClient(request).user_accounts(request.user)
            if "urls.msparp" in request.registry.settings:
                msparp_accounts = MSPARPClient(request).user_accounts(request.user)
        except RequestException:
            pass

    tumblr_accounts = []
    for account in request.user.tumblr_accounts:
        oauth_token_session = OAuth1Session(
            request.registry.settings["tumblr.oauth_key"],
            client_secret=request.registry.settings["tumblr.oauth_secret"],
            resource_owner_key=account.oauth_key,
            resource_owner_secret=account.oauth_secret,
        )
        user_info = oauth_token_session.get("https://api.tumblr.com/v2/user/info")
        # TODO error handling
        tumblr_accounts.append((account, user_info.json()["response"]["user"]))

    return {
        "cherubplay_accounts": cherubplay_accounts,
        "msparp_accounts": msparp_accounts,
        "tumblr_accounts": tumblr_accounts,
    }


@view_config(route_name="account.change_password", request_method="POST", renderer="json")
def change_password(request):
    if (
        not request.POST.get("old_password")
        or not request.POST.get("new_password")
        or not request.POST.get("new_password_again")
    ):
        return error_response(request, "Please fill in all the fields.")

    if request.POST["new_password"] != request.POST["new_password_again"]:
        return error_response(request, "Those passwords didn't match.")

    if not request.user.check_password(request.POST["old_password"]):
        return error_response(request, "That's the wrong password.")

    request.user.set_password(request.POST["new_password"])
    return success_response(request, "Your password has been changed.")


@view_config(route_name="account.change_email", request_method="POST", renderer="json")
def change_email(request):
    if not request.POST.get("email_address"):
        return error_response(request, "Please enter an email address.")

    email_address = request.POST["email_address"].strip()[:User.email_address.type.length]
    if not User.email_address.type.regex.match(email_address):
        return error_response(request, "Please enter a valid email address.")

    if (
        request.db.query(func.count("*")).select_from(User)
        .filter(func.lower(User.email_address) == email_address.lower()).scalar()
    ):
        return error_response(request, "There's already an account with that email address.")

    send_email(request, "verify", request.user, email_address)

    return success_response(request, "Check your email and click the link to verify your new address.")


@view_config(route_name="account.tumblr", request_method="POST")
def tumblr(request):
    oauth_session = OAuth1Session(
        request.registry.settings["tumblr.oauth_key"],
        client_secret=request.registry.settings["tumblr.oauth_secret"],
    )

    fetch_response = oauth_session.fetch_request_token("https://www.tumblr.com/oauth/request_token")
    if (
        not fetch_response.get("oauth_token")
        or not fetch_response.get("oauth_token_secret")
        or not fetch_response.get("oauth_callback_confirmed")
    ):
        raise HTTPBadRequest

    # TODO store this somewhere more temporary
    request.session["request_key"] = fetch_response["oauth_token"]
    request.session["request_secret"] = fetch_response["oauth_token_secret"]

    return HTTPFound(oauth_session.authorization_url("https://www.tumblr.com/oauth/authorize"))


@view_config(route_name="account.tumblr.callback", request_method="GET")
def tumblr_callback(request):
    print("LOL")

    if (
        not request.GET.get("oauth_token")
        or not request.GET.get("oauth_verifier")
        or not request.session.get("request_key")
        or not request.session.get("request_secret")
        or request.GET["oauth_token"] != request.session["request_key"]
    ):
        raise HTTPBadRequest

    request_token_session = OAuth1Session(
        request.registry.settings["tumblr.oauth_key"],
        client_secret=request.registry.settings["tumblr.oauth_secret"],
        resource_owner_key=request.session["request_key"],
        resource_owner_secret=request.session["request_secret"],
        verifier=request.GET["oauth_verifier"],
    )

    oauth_tokens = request_token_session.fetch_access_token("https://www.tumblr.com/oauth/access_token")

    oauth_token_session = OAuth1Session(
        request.registry.settings["tumblr.oauth_key"],
        client_secret=request.registry.settings["tumblr.oauth_secret"],
        resource_owner_key=oauth_tokens["oauth_token"],
        resource_owner_secret=oauth_tokens["oauth_token_secret"],
    )

    user_info = oauth_token_session.get("https://api.tumblr.com/v2/user/info")

    request.db.add(TumblrAccount(
        user=request.user,
        oauth_key=oauth_tokens["oauth_token"],
        oauth_secret=oauth_tokens["oauth_token_secret"],
        last_known_url=user_info.json()["response"]["user"]["name"],
    ))

    return HTTPFound(request.route_path("account.settings"))

