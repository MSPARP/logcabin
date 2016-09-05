import math
import requests

from collections import OrderedDict
from markdown import Markdown
from markupsafe import escape
from pyramid.httpexceptions import HTTPBadRequest, HTTPForbidden, HTTPFound, HTTPNotFound
from pyramid.view import view_config
from pyramid.authentication import Authenticated
from requests.exceptions import RequestException

from logcabin.lib.cherubplay import CherubplayClient
from logcabin.lib.msparp import MSPARPClient
from logcabin.models import User, Log, CherubplaySource, Chapter, ChapterRevision, Message, MessageRevision, ChapterRevisionMessageRevision


md = Markdown()


"""
@view_config(route_name="upload", renderer="upload/index.mako")
def upload(request):
    cherubplay_chats = OrderedDict()
    msparp_chats = OrderedDict()
    if request.user.email_verified:
        try:
            if "urls.cherubplay" in request.registry.settings:
                cherubplay = CherubplayClient(request)
                cherubplay_chats = OrderedDict([
                    (account["username"], cherubplay.account_chats(account["id"]))
                    for account in cherubplay.user_accounts(request.user)
                ])
            if "urls.msparp" in request.registry.settings:
                msparp = MSPARPClient(request)
                msparp_chats = OrderedDict([
                    (account["username"], msparp.account_chats(account["id"]))
                    for account in msparp.user_accounts(request.user)
                ])
        except RequestException:
            pass
    return {
        "cherubplay_chats": cherubplay_chats,
        "msparp_chats": msparp_chats,
    }


def _get_account_and_log(request, cherubplay):

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


@view_config(route_name="upload.cherubplay", request_method="GET", permission="import", renderer="upload/cherubplay.mako")
def upload_cherubplay_get(request):
    cherubplay = CherubplayClient(request)
    user_account, chat_log = _get_account_and_log(request, cherubplay)
    return {
        "account": user_account,
        "chat_log": chat_log,
    }


@view_config(route_name="upload.cherubplay", request_method="POST", permission="import")
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

    new_chapter = Chapter(log=new_log, number=1, name="Chapter 1", creator=request.user)
    request.db.add(new_chapter)
    request.db.flush()

    new_chapter_revision = ChapterRevision(chapter=new_chapter, creator=request.user)

    page_count = math.ceil(float(chat_log["message_count"]) / len(chat_log["messages"]))

    for number, message in enumerate(chat_log["messages"], 1):
        if message["type"] == "ooc" and "include_ooc" not in request.POST:
            continue
        new_message = Message(
            creator=request.user,
            created=message["posted"],
            imported_from="cherubplay:%s" % message["id"],
        )
        request.db.add(new_message)
        request.db.flush()
        new_message_revision = MessageRevision(
            message=new_message,
            creator=request.user,
            created=message["edited"],
            text=message["text"],
            html_text=md.convert(escape(message["text"])),

        )
        request.db.add(new_message_revision)
        request.db.flush()
        request.db.add(ChapterRevisionMessageRevision(
            chapter_revision=new_chapter_revision,
            message_revision=new_message_revision,
            number=number,
        ))

    # TODO move all this to celery
    for page_number in range(2, page_count + 1):
        page = cherubplay.chat_log(user_account["id"], request.matchdict["url"], page=page_number)
        for number, message in enumerate(page["messages"], number):
            if message["type"] == "ooc" and "include_ooc" not in request.POST:
                continue
            new_message = Message(
                creator=request.user,
                created=message["posted"],
                imported_from="cherubplay:%s" % message["id"],
            )
            request.db.add(new_message)
            request.db.flush()
            new_message_revision = MessageRevision(
                message=new_message,
                creator=request.user,
                created=message["edited"],
                text=message["text"],
                html_text=md.convert(escape(message["text"])),
            )
            request.db.add(new_message_revision)
            request.db.flush()
            request.db.add(ChapterRevisionMessageRevision(
                chapter_revision=new_chapter_revision,
                message_revision=new_message_revision,
                number=number,
            ))

    return HTTPFound(request.route_path("logs.chapter", log_id=new_log.id, number=1))


@view_config(route_name="upload.msparp", request_method="GET", permission="import", renderer="upload/msparp.mako")
def upload_msparp_get(request):
    msparp = MSPARPClient(request)

    user_account = None
    for account in msparp.user_accounts(request.user):
        if account["username"] == request.matchdict["username"]:
            user_account = account

    if user_account is None:
        raise HTTPNotFound

    chat_log = msparp.chat_log(user_account["id"], request.matchdict["url"])

    # TODO make group chats work
    if not chat_log:
        raise HTTPNotFound

    return {
        "account": user_account,
        "chat_log": chat_log,
    }
"""
