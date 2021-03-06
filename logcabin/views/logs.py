from datetime import datetime

from markdown import Markdown
from markupsafe import escape
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.view import view_config
from requests.exceptions import ConnectionError
from sqlalchemy import and_, func, literal
from sqlalchemy.orm import joinedload

from logcabin.lib.cherubplay import CherubplayClient
from logcabin.models import Chapter, ChapterRevision, ChapterRevisionMessageRevision, Favorite, Log, Message, MessageRevision


md = Markdown()


@view_config(route_name="logs.new", request_method="GET", renderer="logs/new.mako")
def logs_new_get(request):
    return {}


@view_config(route_name="logs.new", request_method="POST", renderer="logs/new.mako")
def logs_new_post(request):
    name = request.POST.get("name", "").strip()[:Log.name.type.length]
    if not name:
        return {"error": "name"}

    if request.POST.get("rating") not in Log.ratings:
        raise Exception
        return {"error": "rating"}

    summary = request.POST.get("summary", "").strip()
    messages = []

    for message in request.POST.get("message", "").replace("\r\n", "\n").split("\n\n"):
        message = message.strip()
        if message:
            messages.append(message)

    if not messages:
        return {"error": "message"}

    new_log = Log(
        name=name,
        summary=summary if summary else None,
        creator=request.user,
        posted_anonymously="posted_anonymously" in request.POST,
        rating=request.POST["rating"]
    )
    request.db.add(new_log)
    request.db.flush()

    new_chapter = Chapter(log=new_log, number=1, name="Chapter 1", creator=request.user)
    request.db.add(new_chapter)
    request.db.flush()

    new_chapter_revision = ChapterRevision(chapter=new_chapter, creator=request.user)

    for number, message in enumerate(messages, 1):
        new_message = Message(creator=request.user)
        request.db.add(new_message)
        request.db.flush()
        new_message_revision = MessageRevision(
            message=new_message,
            creator=request.user,
            text=message,
            html_text=md.convert(escape(message)),

        )
        request.db.add(new_message_revision)
        request.db.flush()
        request.db.add(ChapterRevisionMessageRevision(
            chapter_revision=new_chapter_revision,
            message_revision=new_message_revision,
            number=number,
        ))

    return HTTPFound(request.route_path("logs.log", log_id=new_log.id))


@view_config(route_name="logs.log", permission=NO_PERMISSION_REQUIRED, renderer="logs/log.mako")
@view_config(route_name="logs.log.ext", extension="json", permission=NO_PERMISSION_REQUIRED, renderer="json")
@view_config(route_name="logs.log.ext", extension="yaml", permission=NO_PERMISSION_REQUIRED, renderer="yaml")
def logs_log(context, request):
    chapter_count = request.db.query(func.count("*")).select_from(Chapter).filter(Chapter.log_id == context.id).scalar()
    if chapter_count <= 10:
        oldest_chapters = request.db.query(Chapter).filter(Chapter.log_id == context.id).order_by(Chapter.number).all()
        newest_chapters = []
    else:
        oldest_chapters = request.db.query(Chapter).filter(Chapter.log_id == context.id).order_by(Chapter.number).limit(5).all()
        newest_chapters = request.db.query(Chapter).filter(Chapter.log_id == context.id).order_by(Chapter.number.desc()).limit(5).all()
        newest_chapters.reverse()

    sources = []
    if request.user == context.creator:
        cherubplay = None
        user_accounts = None
        for source in context.sources:
            if source.type == "cherubplay":
                try:
                    if cherubplay is None or user_accounts is None:
                        cherubplay = CherubplayClient(request)
                        user_accounts = cherubplay.user_accounts(request.user)
                    account = [account for account in user_accounts if account["id"] == source.account_id][0]
                    sources.append((source, cherubplay.chat_log(source.account_id, source.url), account))
                except (ConnectionError, IndexError):
                    continue
            else:
                raise NotImplementedError

    return {
        "log": context,
        "chapter_count": chapter_count,
        "oldest_chapters": oldest_chapters,
        "newest_chapters": newest_chapters,
        "sources": sources,
        "own_favorite": request.db.query(Favorite).filter(and_(
            Favorite.log_id == context.id,
            Favorite.user_id == request.user.id,
        )).first() if request.user else None,
        "favorites": (
            request.db.query(Favorite)
            .filter(Favorite.log_id == context.id)
            .order_by(Favorite.created.desc())
            .options(joinedload(Favorite.user))
            .limit(10).all()
        ),
    }


@view_config(route_name="logs.chapters", permission=NO_PERMISSION_REQUIRED, renderer="logs/chapters.mako")
@view_config(route_name="logs.chapters.ext", extension="json", permission=NO_PERMISSION_REQUIRED, renderer="json")
@view_config(route_name="logs.chapters.ext", extension="yaml", permission=NO_PERMISSION_REQUIRED, renderer="yaml")
def logs_chapters(context, request):
    return {"chapters": request.db.query(Chapter).filter(Chapter.log_id == context.id).order_by(Chapter.number).all()}


@view_config(route_name="logs.chapter", permission=NO_PERMISSION_REQUIRED, renderer="logs/chapter.mako")
@view_config(route_name="logs.chapter.ext", extension="json", permission=NO_PERMISSION_REQUIRED, renderer="json")
@view_config(route_name="logs.chapter.ext", extension="yaml", permission=NO_PERMISSION_REQUIRED, renderer="yaml")
def logs_chapter_get(context, request):
    return {
        "chapter_revision": context.latest_revision,
        "messages": (
            request.db.query(MessageRevision)
            .select_from(ChapterRevisionMessageRevision)
            .join(ChapterRevisionMessageRevision.message_revision)
            .join(MessageRevision.message)
            .filter(ChapterRevisionMessageRevision.chapter_revision_id == context.latest_revision.id)
            .options(joinedload(MessageRevision.message))
            .order_by(ChapterRevisionMessageRevision.number).all()
        ),
    }


@view_config(route_name="logs.chapter", request_method="POST", permission="edit")
def logs_chapter_post(context, request):

    # TODO edit locking or some shit
    messages = (
        request.db.query(MessageRevision, Message)
        .select_from(ChapterRevisionMessageRevision)
        .join(ChapterRevisionMessageRevision.message_revision)
        .join(MessageRevision.message)
        .filter(ChapterRevisionMessageRevision.chapter_revision_id == context.latest_revision.id)
        .order_by(ChapterRevisionMessageRevision.number)
    )

    deleted_message_revisions = set()
    changed_message_revisions = []

    for message_revision, message in messages:
        if request.POST.get("delete_" + str(message.id)):
            deleted_message_revisions.add(message_revision.id)
        elif request.POST.get("edit_" + str(message.id)):
            new_text = request.POST["edit_" + str(message.id)].strip()
            if new_text == message_revision.text:
                continue
            new_message_revision = MessageRevision(
                message=message,
                creator=request.user,
                text=new_text,
                html_text=md.convert(escape(new_text)),
            )
            request.db.add(new_message_revision)
            request.db.flush()
            changed_message_revisions.append((message_revision.id, new_message_revision.id))

    if deleted_message_revisions or changed_message_revisions:
        # Create a new chapter revision by copying the message revision ids from the old one...
        new_chapter_revision = ChapterRevision(chapter=context, creator=request.user, created=datetime.now())
        context.log.last_modified = new_chapter_revision.created
        request.db.flush()

        message_revision_query = request.db.query(
            literal(new_chapter_revision.id),
            ChapterRevisionMessageRevision.number,
            ChapterRevisionMessageRevision.message_revision_id,
        ).filter(ChapterRevisionMessageRevision.chapter_revision_id == context.latest_revision.id)
        if deleted_message_revisions:
            message_revision_query = message_revision_query.filter(
                ~ChapterRevisionMessageRevision.message_revision_id.in_(deleted_message_revisions),
            )

        request.db.execute(ChapterRevisionMessageRevision.__table__.insert().from_select(
            ["chapter_revision_id", "number", "message_revision_id"],
            message_revision_query,
        ))

        # ...then swap out the message revision ids where necessary.
        for old_message_revision_id, new_message_revision_id in changed_message_revisions:
            request.db.query(ChapterRevisionMessageRevision).filter(and_(
                ChapterRevisionMessageRevision.chapter_revision_id == new_chapter_revision.id,
                ChapterRevisionMessageRevision.message_revision_id == old_message_revision_id
            )).update({"message_revision_id": new_message_revision_id})

    return HTTPFound(request.route_path("logs.chapter", log_id=context.log_id, number=context.number))


@view_config(route_name="logs.chapter.message", request_method="GET", permission="edit", renderer="logs/message.mako")
@view_config(route_name="logs.chapter.message.ext", extension="json", request_method="GET", permission="edit", renderer="json")
@view_config(route_name="logs.chapter.message.ext", extension="yaml", request_method="GET", permission="edit", renderer="yaml")
def logs_chapter_message_get(context, request):

    try:
        message_revision = (
            request.db.query(MessageRevision)
            .select_from(ChapterRevisionMessageRevision)
            .join(ChapterRevisionMessageRevision.message_revision)
            # TODO join messages
            .filter(and_(
                ChapterRevisionMessageRevision.chapter_revision_id == context.latest_revision.id,
                MessageRevision.message_id == int(request.matchdict.get("message_id")),
            )).one()
        )
    except (ValueError, NoResultFound):
        raise HTTPNotFound

    if request.matched_route.name == "logs.chapter.message":
        return {"message_revision": message_revision}
    return message_revision


@view_config(route_name="logs.favorite", request_method="POST")
def logs_favorite(context, request):
    existing_favorite = request.db.query(Favorite).filter(and_(
        Favorite.log_id == context.id,
        Favorite.user_id == request.user.id,
    )).first()
    if not existing_favorite:
        request.db.add(Favorite(log=context, user=request.user))
    return HTTPFound(request.headers.get("Referer") or request.route_path("logs.log", log_id=context.id))


@view_config(route_name="logs.unfavorite", request_method="POST")
def logs_unfavorite(context, request):
    request.db.query(Favorite).filter(and_(
        Favorite.log_id == context.id,
        Favorite.user_id == request.user.id,
    )).delete()
    return HTTPFound(request.headers.get("Referer") or request.route_path("logs.log", log_id=context.id))

