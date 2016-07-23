from pyramid.authentication import Authenticated
from pyramid.renderers import render_to_response
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.view import view_config, forbidden_view_config, notfound_view_config

from logcabin.models import User


@view_config(route_name="home", renderer="home_unauthenticated.mako", permission=NO_PERMISSION_REQUIRED)
def home_unauthenticated(request):
    return {}


@view_config(route_name="home", renderer="home.mako", effective_principals=Authenticated)
def home(request):
    return {}


@forbidden_view_config()
def forbidden(request):
    if request.user:
        response = render_to_response("errors/403.mako", {}, request)
    else:
        response = render_to_response("home_unauthenticated.mako", {}, request)
    response.status_int = 403
    return response


@notfound_view_config()
def notfound(request):
    response = render_to_response("errors/404.mako", {}, request)
    response.status_int = 404
    return response

