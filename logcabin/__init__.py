import datetime
import transaction

from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.config import Configurator
from pyramid.authentication import Authenticated, Everyone
from sqlalchemy import engine_from_config
from sqlalchemy.orm.exc import NoResultFound

from logcabin.models import Base, Session, User
from logcabin.resources import get_user


class LogCabinAuthenticationPolicy(SessionAuthenticationPolicy):
    def callback(self, userid, request):
        if not request.user:
            return None
        return {
            "banned": ("banned",),
            "guest": (),
            "active": ("active",),
        }[request.user.status]

    def remember(self, request, userid, **kwargs):
        request.session.adjust_timeout_for_session(2592000)
        return super().remember(request, userid, **kwargs)

    def forget(self, request):
        ret = super().forget(request)
        request.session.invalidate()
        return ret


def request_user(request):
    if not request.unauthenticated_userid:
        return None

    try:
        user = Session.query(User).filter(User.id == request.unauthenticated_userid).one()
    except NoResultFound:
        return None

    user.last_online = datetime.datetime.now()
    user.last_ip = request.environ["REMOTE_ADDR"]
    if user.status == "banned" and user.unban_date is not None:
        if user.unban_delta.total_seconds() < 0:
            user.unban_date = None
            user.status = "active"
    # The ACL stuff means the user object belongs to a different
    # transaction to the rest of the request, so we have to manually
    # commit it here (and set the Session to not expire on commit).
    # TODO consider not using scoped_session and just making the Session a request property
    transaction.commit()

    return user


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, "sqlalchemy.")
    Session.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(
        settings=settings,
        authentication_policy=LogCabinAuthenticationPolicy(),
    )
    config.include("pyramid_mako")

    config.add_request_method(request_user, 'user', reify=True)

    config.add_static_view("static", "static", cache_max_age=3600)

    config.add_route("home", "/")

    config.add_route("account.register", "/account/register")
    config.add_route("account.log_in", "/account/log_in")
    config.add_route("account.log_out", "/account/log_out")
    config.add_route("account.settings", "/account/settings")
    config.add_route("account.change_password", "/account/change_password")

    config.add_route("users.profile", "/users/{username}", factory=get_user)
    config.add_route("users.logs", "/users/{username}/logs", factory=get_user)
    config.add_route("users.favorites", "/users/{username}/favorites", factory=get_user)
    config.add_route("users.subscriptions", "/users/{username}/subscriptions", factory=get_user)

    config.add_route("logs.log", "/logs/{id}")

    config.scan()
    return config.make_wsgi_app()

