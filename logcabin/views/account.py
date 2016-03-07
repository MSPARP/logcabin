from pyramid.httpexceptions import HTTPBadRequest, HTTPFound
from pyramid.security import forget, remember
from pyramid.view import view_config
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound

from logcabin.models import Session, User


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


@view_config(route_name="account.register", request_method="POST", renderer="json")
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
        Session.query(func.count("*")).select_from(User)
        .filter(func.lower(User.username) == username.lower()).scalar()
    ):
        return error_response(request, "There's already an account called %s. Please choose a different username." % username)

    if (
        Session.query(func.count("*")).select_from(User)
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
    Session.add(new_user)
    Session.flush()

    remember(request, new_user.id)
    return success_response(request, "Welcome to Log Cabin!")


@view_config(route_name="account.log_in", request_method="POST", renderer="json")
def log_in(request):
    if not request.POST.get("username") or not request.POST.get("password"):
        return error_response(request, "Please fill in all the fields.")

    try:
        username = request.POST["username"].strip()[:User.username.type.length]
        user = Session.query(User).filter(func.lower(User.username) == username.lower()).one()
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

