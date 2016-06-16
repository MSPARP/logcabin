import requests

from collections import OrderedDict
from pyramid.httpexceptions import HTTPForbidden, HTTPNotFound
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


@view_config(route_name="upload_cherubplay", renderer="upload_cherubplay.mako")
def upload_cherubplay(request):

    if not request.user.email_verified: # TODO make a permission for this
        raise HTTPForbidden

    cherubplay = CherubplayClient(request)

    user_account = None
    for account in cherubplay.user_accounts(request.user):
        if account["username"] == request.matchdict["username"]:
            user_account = account

    if user_account is None:
        raise HTTPNotFound

    chat_log = cherubplay.chat_log(user_account["id"], request.matchdict["url"])

    if not chat_log["messages"]:
        raise HTTPNotFound

    return {
        "account": user_account,
        "chat_log": chat_log,
    }

