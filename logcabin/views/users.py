from feedgen.entry import FeedEntry
from pyramid.view import view_config
from pytz import utc
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
def users_logs(context, request):
    return {
        "recent_logs": (
            Session.query(Log)
            .filter(Log.creator_id == context.id)
            .order_by(Log.last_modified.desc())
            .limit(25).all()
        ),
    }


@view_config(route_name="users.logs.ext", extension="rss", renderer="rss")
@view_config(route_name="users.logs.ext", extension="atom", renderer="atom")
def users_logs_feed(context, request):
    entries = []
    for log in (
        Session.query(Log)
        .filter(Log.creator_id == context.id)
        .order_by(Log.last_modified.desc())
        .limit(25).all()
    ):
        entry = FeedEntry()
        entry.id(str(log.id))
        entry.title(log.name)
        entry.content(log.name)
        entry.published(utc.localize(log.created))
        entries.append(entry)

    return {
        "title": "%s's logs" % context.username,
        "entries": entries,
    }


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


@view_config(route_name="users.favorites.ext", extension="rss", renderer="rss")
@view_config(route_name="users.favorites.ext", extension="atom", renderer="atom")
def users_favorites_feed(context, request):
    entries = []
    for favorite in (
        Session.query(Favorite)
        .filter(Favorite.user_id == context.id)
        .order_by(Favorite.created.desc())
        .options(joinedload(Favorite.log).joinedload(Log.creator))
        .limit(25).all()
    ):
        entry = FeedEntry()
        entry.id(str(favorite.log.id))
        entry.title("%s favorited %s." % (context.username, favorite.log.name))
        entry.content("%s favorited %s." % (context.username, favorite.log.name))
        entry.published(utc.localize(favorite.created))
        entries.append(entry)

    return {
        "title": "%s's favorites" % context.username,
        "entries": entries,
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


@view_config(route_name="users.subscriptions.ext", extension="rss", renderer="rss")
@view_config(route_name="users.subscriptions.ext", extension="atom", renderer="atom")
def users_subscriptions_feed(context, request):
    entries = []
    for subscription in (
        Session.query(LogSubscription)
        .filter(LogSubscription.user_id == context.id)
        .order_by(LogSubscription.created.desc())
        .options(joinedload(LogSubscription.log).joinedload(Log.creator))
        .limit(25).all()
    ):
        entry = FeedEntry()
        entry.id(str(subscription.log.id))
        entry.title("%s subscribed to %s." % (context.username, subscription.log.name))
        entry.content("%s subscribed to %s." % (context.username, subscription.log.name))
        entry.published(utc.localize(subscription.created))
        entries.append(entry)

    return {
        "title": "%s's subscriptions" % context.username,
        "entries": entries,
    }

