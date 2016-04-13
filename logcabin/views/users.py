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
            .limit(10)
        ),
        "favorites": (
            Session.query(Favorite)
            .filter(Favorite.user_id == context.id)
            .order_by(Favorite.created.desc())
            .options(joinedload(Favorite.log).joinedload(Log.creator))
            .limit(10)
        ),
        "log_subscriptions": (
            Session.query(LogSubscription)
            .filter(LogSubscription.user_id == context.id)
            .order_by(LogSubscription.created.desc())
            .options(joinedload(LogSubscription.log).joinedload(Log.creator))
            .limit(10)
        ),
    }

