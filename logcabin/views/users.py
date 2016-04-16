from pyramid.view import view_config
from sqlalchemy.orm import joinedload

from logcabin.models import Session, Favorite, Log, LogSubscription


@view_config(route_name="users.profile", renderer="users/profile.mako")
def users_profile(context, request):
    return {
        "recent_logs": (
            Session.query(Log)
            .filter(Log.creator_id == context.id)
            .order_by(Log.last_modified.desc())
            .limit(10).all()
        ),
        "favorites": (
            Session.query(Favorite)
            .filter(Favorite.user_id == context.id)
            .order_by(Favorite.created.desc())
            .options(joinedload(Favorite.log).joinedload(Log.creator))
            .limit(10).all()
        ),
        "log_subscriptions": (
            Session.query(LogSubscription)
            .filter(LogSubscription.user_id == context.id)
            .order_by(LogSubscription.created.desc())
            .options(joinedload(LogSubscription.log).joinedload(Log.creator))
            .limit(10).all()
        ),
    }


@view_config(route_name="users.logs", renderer="users/logs.mako")
@view_config(route_name="users.logs.ext", extension="json", renderer="json")
@view_config(route_name="users.logs.ext", extension="yaml", renderer="yaml")
@view_config(route_name="users.logs.ext", extension="rss", renderer="rss")
def users_logs(context, request):
    recent_logs = (
        Session.query(Log)
        .filter(Log.creator_id == context.id)
        .order_by(Log.last_modified.desc())
        .limit(25).all()
    )

    if request.matchdict.get("ext") == "rss":
        return {
            "title": "%s's logs" % context.username,
            "items": recent_logs,
        }

    return {"recent_logs": recent_logs}


@view_config(route_name="users.favorites", renderer="users/favorites.mako")
@view_config(route_name="users.favorites.ext", extension="json", renderer="json")
@view_config(route_name="users.favorites.ext", extension="yaml", renderer="yaml")
def users_favorites(context, request):
    return {
        "favorites": (
            Session.query(Favorite)
            .filter(Favorite.user_id == context.id)
            .order_by(Favorite.created.desc())
            .options(joinedload(Favorite.log).joinedload(Log.creator))
            .limit(25).all()
        ),
    }


@view_config(route_name="users.subscriptions", renderer="users/subscriptions.mako")
@view_config(route_name="users.subscriptions.ext", extension="json", renderer="json")
@view_config(route_name="users.subscriptions.ext", extension="yaml", renderer="yaml")
def users_subscriptions(context, request):
    return {
        "log_subscriptions": (
            Session.query(LogSubscription)
            .filter(LogSubscription.user_id == context.id)
            .order_by(LogSubscription.created.desc())
            .options(joinedload(LogSubscription.log).joinedload(Log.creator))
            .limit(25).all()
        ),
    }

