from pyramid.view import view_config

from logcabin.models import Session, User


@view_config(route_name='home', renderer='templates/mytemplate.pt')
def my_view(request):
    return {'project': 'logcabin'}

