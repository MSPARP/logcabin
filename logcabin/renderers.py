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
        feed.id(system["request"].url)
        feed.title(value["title"])
        feed.description("Log Cabin")
        feed.link(rel="self", href=system["request"].url)
        feed.language("en")

        for entry in value["entries"]:
            feed.add_entry(entry)

        if system["renderer_name"] == "rss":
            system["request"].response.headers["Content-type"] = "application/rss+xml; charset=UTF-8"
            return feed.rss_str()
        else:
            system["request"].response.headers["Content-type"] = "application/atom+xml; charset=UTF-8"
            return feed.atom_str()

