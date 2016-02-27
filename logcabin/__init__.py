from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.config import Configurator
from pyramid.authentication import Authenticated, Everyone
from sqlalchemy import engine_from_config
from sqlalchemy.orm.exc import NoResultFound

from logcabin.models import Base, Session, User


def request_user(request):
    if not request.unauthenticated_userid:
        return None
    try:
        return Session.query(User).filter(User.id == request.unauthenticated_userid).one()
    except NoResultFound:
        pass
    return None


def authentication_callback(userid, request):
    if not request.user:
        return None
    return {
        "banned": ("banned",),
        "guest": (),
        "active": ("active",),
    }[request.user.status]


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, "sqlalchemy.")
    Session.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(
        settings=settings,
        authentication_policy=SessionAuthenticationPolicy(callback=authentication_callback),
    )
    config.include("pyramid_mako")

    config.add_request_method(request_user, 'user', reify=True)

    config.add_static_view("static", "static", cache_max_age=3600)

    config.add_route("home", "/")

    config.add_route("account.register", "/account/register")
    config.add_route("account.log_in", "/account/log_in")
    config.add_route("account.log_out", "/account/log_out")

    config.scan()
    return config.make_wsgi_app()

