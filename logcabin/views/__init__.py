from pyramid.view import view_config
from pyramid.authentication import Authenticated
from pyramid.security import NO_PERMISSION_REQUIRED

from logcabin.models import User


@view_config(route_name="home", renderer="home_unauthenticated.mako", permission=NO_PERMISSION_REQUIRED)
def home_unauthenticated(request):
    return {}


@view_config(route_name="home", renderer="home.mako", effective_principals=Authenticated)
def home(request):
    return {}

