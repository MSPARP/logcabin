import requests


class CherubplayClient(object):
    def __init__(self, request):
        self.settings = request.registry.settings
        self.session = requests.Session()
        if "pyramid_debugtoolbar" in self.settings["pyramid.includes"]:
            self.session.verify = False
        self.session.cert = (
            self.settings["certificates.client_certificate"],
            self.settings["certificates.client_key"],
        )

    def user_accounts(self, user):
        api_request = self.session.get(
            self.settings["urls.cherubplay"] + "/api/users.json",
            params={"email_address": user.email_address},
        )
        if api_request.status_code == 200:
            return api_request.json()["users"]

