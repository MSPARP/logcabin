from requests import Session


class CherubplayClient(object):
    def __init__(self, request):
        self.settings = request.registry.settings
        self.session = Session()
        if "pyramid_debugtoolbar" in self.settings["pyramid.includes"]:
            self.session.verify = False
        self.session.cert = (
            self.settings["certificates.client_certificate"],
            self.settings["certificates.client_key"],
        )

    def user_accounts(self, user):
        if not user.email_verified:
            return []
        api_request = self.session.get(
            self.settings["urls.cherubplay"] + "/api/users.json",
            params={"email_address": user.email_address},
        )
        if api_request.status_code == 200:
            return api_request.json()["users"]
        return []

    def account_chats(self, account_id, page=1):
        api_request = self.session.get(
            self.settings["urls.cherubplay"] + "/chats.json",
            headers={"X-Cherubplay-User-Id": account_id},
            params={"page": page},
        )
        if api_request.status_code == 200:
            return api_request.json()["chats"]
        return []

    def chat_log(self, account_id, url, page=1):
        api_request = self.session.get(
            self.settings["urls.cherubplay"] + "/chats/" + url + ".json",
            headers={"X-Cherubplay-User-Id": account_id},
            params={"page": page},
        )
        if api_request.status_code == 200:
            return api_request.json()
        return None

