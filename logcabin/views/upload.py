import requests

from collections import OrderedDict
from pyramid.view import view_config
from pyramid.authentication import Authenticated
from requests.exceptions import RequestException

from logcabin.models import User


@view_config(route_name="upload", renderer="upload.mako")
def upload(request):
    cherubplay_chats = OrderedDict()
    if request.user.email_verified:
        try:
            if "urls.cherubplay" in request.registry.settings:
                cherubplay_request = requests.get(
                    request.registry.settings["urls.cherubplay"] + "/api/users.json",
                    params={"email_address": request.user.email_address},
                    verify=False if "pyramid_debugtoolbar" in request.registry.settings["pyramid.includes"] else None,
                    cert=(request.registry.settings["certificates.client_certificate"], request.registry.settings["certificates.client_key"]),
                )
                if cherubplay_request.status_code == 200:
                    cherubplay_accounts = cherubplay_request.json()["users"]
                    for account in cherubplay_accounts:
                        chat_request = requests.get(
                            request.registry.settings["urls.cherubplay"] + "/chats.json",
                            headers={"X-Cherubplay-User-Id": account["id"]},
                            verify=False if "pyramid_debugtoolbar" in request.registry.settings["pyramid.includes"] else None,
                            cert=(request.registry.settings["certificates.client_certificate"], request.registry.settings["certificates.client_key"]),
                        )
                        if chat_request.status_code == 200:
                            cherubplay_chats[account["username"]] = chat_request.json()["chats"]
        except RequestException:
            pass
    return {"cherubplay_chats": cherubplay_chats}

