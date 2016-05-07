from pyramid.view import view_config
from pyramid.authentication import Authenticated

from logcabin.models import User


@view_config(route_name="home", renderer="home_unauthenticated.mako")
def home_unauthenticated(request):
    return {}


@view_config(route_name="home", renderer="home.mako", effective_principals=Authenticated)
def home(request):
    return {}

