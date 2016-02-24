from pyramid.httpexceptions import HTTPBadRequest, HTTPFound
from pyramid.view import view_config
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound

from logcabin.models import Session, User


@view_config(route_name="account.log_in", request_method="POST")
def log_in(request):
    if not request.POST.get("username") or not request.POST.get("password"):
        raise HTTPBadRequest

    try:
        username = request.POST["username"].strip().lower()[:User.username.type.length]
        user = Session.query(User).filter(func.lower(User.username) == username).one()
    except NoResultFound:
        request.session.flash("There isn't an account called %s." % username)
        return HTTPFound(request.headers.get("Referer") or request.route_path("home"))

    if user.check_password(request.POST["password"]):
        request.session.flash("Welcome to log cabin!")
        request.session["user_id"] = user.id
    else:
        request.session.flash("That's the wrong password.")

    return HTTPFound(request.headers.get("Referer") or request.route_path("home"))


@view_config(route_name="account.log_out", request_method="POST")
def log_out(request):
    request.session.invalidate()
    request.session.flash("we'll miss u :'(")
    return HTTPFound(request.route_path("home"))

