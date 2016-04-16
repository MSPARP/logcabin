from camel import Camel, CamelRegistry
from datetime import datetime
from pyramid.renderers import JSON

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
        print("info", info)

    def __call__(self, value, system):
        print("value", value)
        print("system", system)
        system["request"].response.headers["Content-type"] = "application/yaml; charset=UTF-8"
        return camel.dump(value)

