import datetime
import transaction

from pyramid.authentication import Authenticated, Everyone, SessionAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPFound
from sqlalchemy import engine_from_config
from sqlalchemy.orm.exc import NoResultFound

from logcabin.models import Base, Session, Resource, User
from logcabin.resources import get_user, get_log, get_chapter


class LogCabinAuthenticationPolicy(SessionAuthenticationPolicy):
    def callback(self, userid, request):
        if not request.user:
            return None
        principals = [Authenticated]
        if request.user.status != "guest":
            principals.append(request.user.status)
        if request.user.status == "active" and request.user.is_admin:
            principals.append("admin")
        return principals

    def remember(self, request, userid, **kwargs):
        request.session.adjust_timeout_for_session(2592000)
        return super().remember(request, userid, **kwargs)

    def forget(self, request):
        ret = super().forget(request)
        request.session.invalidate()
        return ret


class LogCabinRootFactory(Resource):
    def __init__(self, *args):
        pass


def request_db(request):
    db = Session()
    @request.add_finished_callback
    def close_db(request):
        db.close()
    return db


def request_user(request):
    if not request.unauthenticated_userid:
        return None

    try:
        user = request.db.query(User).filter(User.id == request.unauthenticated_userid).one()
    except NoResultFound:
        return None

    user.last_online = datetime.datetime.now()
    user.last_ip = request.environ["REMOTE_ADDR"]
    if user.status == "banned" and user.unban_date is not None:
        if user.unban_delta.total_seconds() < 0:
            user.unban_date = None
            user.status = "active"

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
        authorization_policy=ACLAuthorizationPolicy(),
        root_factory=LogCabinRootFactory,
    )
    config.include("pyramid_mako")

    config.add_request_method(request_db, 'db', reify=True)
    config.add_request_method(request_user, 'user', reify=True)

    config.include("logcabin.lib.formats")

    config.add_static_view("static", "static", cache_max_age=3600)

    config.add_route("home", "/")

    config.add_route("account.register", "/account/register")
    config.add_route("account.log_in", "/account/log_in")
    config.add_route("account.log_out", "/account/log_out")
    config.add_route("account.forgot_password", "/account/forgot_password")
    config.add_route("account.reset_password", "/account/reset_password")
    config.add_route("account.verify_email", "/account/verify_email")
    config.add_route("account.settings", "/account/settings")
    config.add_route("account.change_password", "/account/change_password")
    config.add_route("account.change_email", "/account/change_email")

    config.add_route("users.profile", "/users/{username}", factory=get_user)
    config.add_ext_route("users.logs", "/users/{username}/logs", factory=get_user)
    config.add_ext_route("users.favorites", "/users/{username}/favorites", factory=get_user)
    config.add_ext_route("users.subscriptions", "/users/{username}/subscriptions", factory=get_user)

    config.add_ext_route("logs.log", "/logs/{log_id:\d+}", factory=get_log)
    config.add_ext_route("logs.chapters", "/logs/{log_id:\d+}/chapters", factory=get_log)
    config.add_ext_route("logs.chapter", "/logs/{log_id:\d+}/chapters/{number:\d+}", factory=get_chapter)

    config.add_ext_route("upload", "/upload")

    config.scan()
    return config.make_wsgi_app()

