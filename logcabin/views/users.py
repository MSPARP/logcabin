from feedgen.entry import FeedEntry
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.view import view_config
from pytz import utc
from sqlalchemy.orm import joinedload

from logcabin.models import Favorite, Log, LogSubscription


@view_config(route_name="users.profile", permission=NO_PERMISSION_REQUIRED, renderer="users/profile.mako")
def users_profile(context, request):

    recent_logs_query = request.db.query(Log).filter(Log.creator_id == context.id)
    if context != request.user:
        recent_logs_query = recent_logs_query.filter(Log.posted_anonymously == False)
    recent_logs_query = recent_logs_query.order_by(Log.last_modified.desc()).limit(10).all()

    return {
        "recent_logs": recent_logs_query,
        "favorites": (
            request.db.query(Favorite)
            .filter(Favorite.user_id == context.id)
            .order_by(Favorite.created.desc())
            .options(joinedload(Favorite.log).joinedload(Log.creator))
            .limit(10).all()
        ),
        "log_subscriptions": (
            request.db.query(LogSubscription)
            .filter(LogSubscription.user_id == context.id)
            .order_by(LogSubscription.created.desc())
            .options(joinedload(LogSubscription.log).joinedload(Log.creator))
            .limit(10).all()
        ),
    }


@view_config(route_name="users.logs", permission=NO_PERMISSION_REQUIRED, renderer="users/logs.mako")
@view_config(route_name="users.logs.ext", extension="json", permission=NO_PERMISSION_REQUIRED, renderer="json")
@view_config(route_name="users.logs.ext", extension="yaml", permission=NO_PERMISSION_REQUIRED, renderer="yaml")
def users_logs(context, request):
    return {
        "recent_logs": (
            request.db.query(Log)
            .filter(Log.creator_id == context.id)
            .order_by(Log.last_modified.desc())
            .limit(25).all()
        ),
    }


@view_config(route_name="users.logs.ext", extension="rss", permission=NO_PERMISSION_REQUIRED, renderer="rss")
@view_config(route_name="users.logs.ext", extension="atom", permission=NO_PERMISSION_REQUIRED, renderer="atom")
def users_logs_feed(context, request):
    entries = []
    for log in (
        request.db.query(Log)
        .filter(Log.creator_id == context.id)
        .order_by(Log.last_modified.desc())
        .limit(25).all()
    ):
        entry = FeedEntry()
        entry.id(str(log.id))
        entry.title(log.name)
        entry.content(log.summary or "No summary.")
        entry.published(utc.localize(log.created))
        entries.append(entry)

    return {
        "title": "%s's logs" % context.username,
        "entries": entries,
    }


@view_config(route_name="users.favorites", permission=NO_PERMISSION_REQUIRED, renderer="users/favorites.mako")
@view_config(route_name="users.favorites.ext", extension="json", permission=NO_PERMISSION_REQUIRED, renderer="json")
@view_config(route_name="users.favorites.ext", extension="yaml", permission=NO_PERMISSION_REQUIRED, renderer="yaml")
def users_favorites(context, request):
    return {
        "favorites": (
            request.db.query(Favorite)
            .filter(Favorite.user_id == context.id)
            .order_by(Favorite.created.desc())
            .options(joinedload(Favorite.log).joinedload(Log.creator))
            .limit(25).all()
        ),
    }


@view_config(route_name="users.favorites.ext", extension="rss", permission=NO_PERMISSION_REQUIRED, renderer="rss")
@view_config(route_name="users.favorites.ext", extension="atom", permission=NO_PERMISSION_REQUIRED, renderer="atom")
def users_favorites_feed(context, request):
    entries = []
    for favorite in (
        request.db.query(Favorite)
        .filter(Favorite.user_id == context.id)
        .order_by(Favorite.created.desc())
        .options(joinedload(Favorite.log).joinedload(Log.creator))
        .limit(25).all()
    ):
        entry = FeedEntry()
        entry.id(str(favorite.log.id))
        entry.title("%s favorited %s." % (context.username, favorite.log.name))
        entry.content(favorite.log.summary or "No summary.")
        entry.published(utc.localize(favorite.created))
        entries.append(entry)

    return {
        "title": "%s's favorites" % context.username,
        "entries": entries,
    }


@view_config(route_name="users.subscriptions", permission=NO_PERMISSION_REQUIRED, renderer="users/subscriptions.mako")
@view_config(route_name="users.subscriptions.ext", extension="json", permission=NO_PERMISSION_REQUIRED, renderer="json")
@view_config(route_name="users.subscriptions.ext", extension="yaml", permission=NO_PERMISSION_REQUIRED, renderer="yaml")
def users_subscriptions(context, request):
    return {
        "log_subscriptions": (
            request.db.query(LogSubscription)
            .filter(LogSubscription.user_id == context.id)
            .order_by(LogSubscription.created.desc())
            .options(joinedload(LogSubscription.log).joinedload(Log.creator))
            .limit(25).all()
        ),
    }


@view_config(route_name="users.subscriptions.ext", extension="rss", permission=NO_PERMISSION_REQUIRED, renderer="rss")
@view_config(route_name="users.subscriptions.ext", extension="atom", permission=NO_PERMISSION_REQUIRED, renderer="atom")
def users_subscriptions_feed(context, request):
    entries = []
    for subscription in (
        request.db.query(LogSubscription)
        .filter(LogSubscription.user_id == context.id)
        .order_by(LogSubscription.created.desc())
        .options(joinedload(LogSubscription.log).joinedload(Log.creator))
        .limit(25).all()
    ):
        entry = FeedEntry()
        entry.id(str(subscription.log.id))
        entry.title("%s subscribed to %s." % (context.username, subscription.log.name))
        entry.content(subscription.log.summary or "No summary.")
        entry.published(utc.localize(subscription.created))
        entries.append(entry)

    return {
        "title": "%s's subscriptions" % context.username,
        "entries": entries,
    }

