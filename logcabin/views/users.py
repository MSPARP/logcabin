from pyramid.view import view_config


@view_config(route_name="users.profile", renderer="users/profile.mako")
def users_profile(context, request):
    return {}

