from pyramid.view import view_config

from logcabin.models import Session, User


@view_config(route_name="home", renderer="home.mako")
def home(request):
    return {}
