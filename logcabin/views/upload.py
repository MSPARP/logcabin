import math
import requests

from collections import OrderedDict
from pyramid.httpexceptions import HTTPBadRequest, HTTPForbidden, HTTPFound, HTTPNotFound
from pyramid.view import view_config
from pyramid.authentication import Authenticated
from requests.exceptions import RequestException

from logcabin.lib.cherubplay import CherubplayClient
from logcabin.models import User, Log, CherubplaySource, Chapter, Message


@view_config(route_name="upload", renderer="upload/index.mako")
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


def _get_account_and_log(request, cherubplay):
    if not request.user.email_verified: # TODO make a permission for this
        raise HTTPForbidden

    user_account = None
    for account in cherubplay.user_accounts(request.user):
        if account["username"] == request.matchdict["username"]:
            user_account = account

    if user_account is None:
        raise HTTPNotFound

    chat_log = cherubplay.chat_log(user_account["id"], request.matchdict["url"])

    if not chat_log["messages"]:
        raise HTTPNotFound

    return user_account, chat_log


@view_config(route_name="upload.cherubplay", renderer="upload/cherubplay.mako", request_method="GET")
def upload_cherubplay_get(request):
    cherubplay = CherubplayClient(request)
    user_account, chat_log = _get_account_and_log(request, cherubplay)
    return {
        "account": user_account,
        "chat_log": chat_log,
    }


@view_config(route_name="upload.cherubplay", request_method="POST")
def upload_cherubplay_post(request):
    cherubplay = CherubplayClient(request)
    user_account, chat_log = _get_account_and_log(request, cherubplay)

    if not request.POST.get("name"):
        raise HTTPBadRequest

    new_log = Log(
        name=request.POST["name"],
        creator=request.user,
    )
    request.db.add(new_log)
    request.db.flush()

    request.db.add(CherubplaySource(
        log=new_log,
        url=chat_log["chat"]["url"],
        account_id=user_account["id"],
        include_ooc="include_ooc" in request.POST,
    ))

    new_chapter = Chapter(log=new_log, number=1, name="Chapter 1", creator_id=request.user.id)
    request.db.add(new_chapter)
    request.db.flush()

    page_count = math.ceil(float(chat_log["message_count"]) / len(chat_log["messages"]))

    for number, message in enumerate(chat_log["messages"], 1):
        if message["type"] == "ooc" and "include_ooc" not in request.POST:
            continue
        request.db.add(Message(
            chapter=new_chapter,
            number=number,
            creator=request.user,
            created=message["posted"],
            last_modified=message["edited"],
            text=message["text"],
        ))

    # TODO move all this to celery
    for page_number in range(2, page_count + 1):
        page = cherubplay.chat_log(user_account["id"], request.matchdict["url"], page=page_number)
        for number, message in enumerate(page["messages"], number):
            if message["type"] == "ooc" and "include_ooc" not in request.POST:
                continue
            request.db.add(Message(
                chapter=new_chapter,
                number=number,
                creator=request.user,
                created=message["posted"],
                last_modified=message["edited"],
                text=message["text"],
            ))

    return HTTPFound(request.route_path("logs.chapter", log_id=new_log.id, number=1))

