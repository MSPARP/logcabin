from camel import Camel, CamelRegistry
from datetime import date, datetime
from feedgen.feed import FeedGenerator
from pyramid.renderers import JSON
from pytz import utc


extension_content_types = {
    "json": "application/json",
    "yaml": "application/yaml",
    "rss": "application/rss+xml",
    "atom": "application/atom+xml",
}


JSONRenderer = JSON()
JSONRenderer.add_adapter(date, lambda obj, request: obj.isoformat())
JSONRenderer.add_adapter(datetime, lambda obj, request: obj.isoformat())


camel_registry = CamelRegistry()
camel = Camel([camel_registry])

class YAMLRenderer(object):
    def __init__(self, info):
        pass

    def __call__(self, value, system):
        system["request"].response.headers["Content-type"] = extension_content_types["yaml"] + "; charset=UTF-8"
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

        if system["renderer_name"] == "atom":
            feed.link([
                {"rel": "alternate", "type": content_type, "href": url}
                for content_type, url in system["request"].extensions
            ])

        for entry in value["entries"]:
            feed.add_entry(entry)

        system["request"].response.headers["Content-type"] = extension_content_types[system["renderer_name"]] + "; charset=UTF-8"

        if system["renderer_name"] == "rss":
            return feed.rss_str(pretty=True)
        else:
            return feed.atom_str(pretty=True)


class ExtensionPredicate(object):
    def __init__(self, extension, config):
        self.extension = extension

    def text(self):
        return "extension == %s" % self.extension

    phash = text

    def __call__(self, context, request):
        # Redirect to no extension if extension is html.
        if request.matchdict["ext"] == "html":
            del request.matchdict["ext"]
            plain_route = request.matched_route.name.split(".ext")[0]
            raise HTTPFound(request.route_path(plain_route, **request.matchdict))
        return request.matchdict["ext"] == self.extension


def add_ext_route(self, name, pattern, **kwargs):
    ext_name = name + ".ext"
    ext_pattern = pattern + ".{ext}"
    self.add_route(ext_name, ext_pattern, **kwargs)
    self.add_route(name, pattern, **kwargs)


def request_extensions(request):
    if not request.matched_route:
        return []

    extension_route = (
        request.matched_route.name if request.matched_route.name.endswith(".ext")
        else request.matched_route.name + ".ext"
    )
    route_introspectable = request.registry.introspector.get("routes", extension_route)
    if not route_introspectable:
        return []

    extensions = []

    if "ext" in request.matchdict:
        matchdict = dict(request.matchdict)
        del matchdict["ext"]
    else:
        matchdict = request.matchdict

    for route in request.registry.introspector.related(route_introspectable):
        if "extension" not in route or route["extension"] == request.matchdict.get("ext"):
            continue
        extensions.append((
            extension_content_types[route["extension"]],
            request.route_url(extension_route, ext=route["extension"], **matchdict),
        ))

    return extensions


def includeme(config):
    config.add_renderer("json", JSONRenderer)
    config.add_renderer("yaml", YAMLRenderer)
    config.add_renderer("rss", FeedRenderer)
    config.add_renderer("atom", FeedRenderer)

    config.add_directive("add_ext_route", add_ext_route)
    config.add_view_predicate("extension", ExtensionPredicate)
    config.add_request_method(request_extensions, 'extensions', reify=True)

