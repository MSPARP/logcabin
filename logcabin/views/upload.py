import requests

from collections import OrderedDict
from pyramid.view import view_config
from pyramid.authentication import Authenticated
from requests.exceptions import RequestException

from logcabin.lib.cherubplay import CherubplayClient
from logcabin.models import User


@view_config(route_name="upload", renderer="upload.mako")
def upload(request):
    cherubplay_chats = OrderedDict()
    if request.user.email_verified:
        try:
            if "urls.cherubplay" in request.registry.settings:
                cherubplay = CherubplayClient(request)
                cherubplay_chats = OrderedDict([
                    (account["username"], cherubplay.account_chats(account["id"]))
                    for account in cherubplay.user_accounts(request.user)
                ])
        except RequestException:
            pass
    return {"cherubplay_chats": cherubplay_chats}

