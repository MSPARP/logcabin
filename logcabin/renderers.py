from camel import Camel, CamelRegistry
from datetime import datetime
from feedgen.feed import FeedGenerator
from pyramid.renderers import JSON
from pytz import utc

from logcabin.models import User, Log, LogSubscription, Favorite


JSONRenderer = JSON()
JSONRenderer.add_adapter(datetime, lambda obj, request: obj.isoformat())


camel_registry = CamelRegistry()
camel_registry.dumper(User, "user", version=None)(User.__json__)
camel_registry.dumper(Log, "log", version=None)(Log.__json__)
camel_registry.dumper(LogSubscription, "log_subscription", version=None)(LogSubscription.__json__)
camel_registry.dumper(Favorite, "favorite", version=None)(Favorite.__json__)
camel = Camel([camel_registry])

class YAMLRenderer(object):
    def __init__(self, info):
        pass

    def __call__(self, value, system):
        system["request"].response.headers["Content-type"] = "application/yaml; charset=UTF-8"
        return camel.dump(value)


class FeedRenderer(object):
    def __init__(self, info):
        pass

    def __call__(self, value, system):
        feed = FeedGenerator()
        feed.title(value["title"])
        feed.description("Log Cabin")
        feed.link(rel="self", href=system["request"].url)
        feed.language("en")
        for item in value["items"]:
            entry = feed.add_entry()
            # TODO custom object -> entry converters
            entry.title(item.name)
            entry.published(utc.localize(item.created))
        return feed.rss_str()

