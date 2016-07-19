from markdown import Markdown
from markupsafe import escape
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.view import view_config
from sqlalchemy import and_, func, literal
from sqlalchemy.orm import joinedload

from logcabin.lib.cherubplay import CherubplayClient
from logcabin.models import Chapter, ChapterRevision, ChapterRevisionMessageRevision, Favorite, Log, Message, MessageRevision


md = Markdown()


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
        cherubplay = CherubplayClient(request)
        user_accounts = cherubplay.user_accounts(request.user)
        for source in context.sources:
            if source.type == "cherubplay":
                try:
                    account = [account for account in user_accounts if account["id"] == source.account_id][0]
                except IndexError:
                    account = None
                sources.append((source, cherubplay.chat_log(source.account_id, source.url), account))
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
    return {"messages": (
        request.db.query(MessageRevision, Message)
        .select_from(ChapterRevisionMessageRevision)
        .join(ChapterRevisionMessageRevision.message_revision)
        .join(MessageRevision.message)
        .filter(ChapterRevisionMessageRevision.chapter_revision_id == context.latest_revision.id)
        .order_by(ChapterRevisionMessageRevision.number)
    )}


@view_config(route_name="logs.chapter", request_method="POST")
def logs_chapter_post(context, request):
    if request.user != context.creator:
        raise HTTPNotFound

    # TODO edit locking or some shit
    messages = (
        request.db.query(MessageRevision, Message)
        .select_from(ChapterRevisionMessageRevision)
        .join(ChapterRevisionMessageRevision.message_revision)
        .join(MessageRevision.message)
        .filter(ChapterRevisionMessageRevision.chapter_revision_id == context.latest_revision.id)
        .order_by(ChapterRevisionMessageRevision.number)
    )

    changed_message_revisions = []

    for message_revision, message in messages:
        if request.POST.get("message_" + str(message.id)):
            new_text = request.POST["message_" + str(message.id)].strip()
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

    if changed_message_revisions:
        # Create a new chapter revision by copying the message revision ids from the old one...
        new_chapter_revision = ChapterRevision(chapter=context, creator=request.user)
        request.db.flush()
        request.db.execute(ChapterRevisionMessageRevision.__table__.insert().from_select(
            ["chapter_revision_id", "number", "message_revision_id"],
            request.db.query(
                literal(new_chapter_revision.id),
                ChapterRevisionMessageRevision.number,
                ChapterRevisionMessageRevision.message_revision_id,
            ).filter(
                ChapterRevisionMessageRevision.chapter_revision_id == context.latest_revision.id,
            ),
        ))
        # ...then swap out the message revision ids where necessary.
        for old_message_revision_id, new_message_revision_id in changed_message_revisions:
            request.db.query(ChapterRevisionMessageRevision).filter(and_(
                ChapterRevisionMessageRevision.chapter_revision_id == new_chapter_revision.id,
                ChapterRevisionMessageRevision.message_revision_id == old_message_revision_id
            )).update({"message_revision_id": new_message_revision_id})

    return HTTPFound(request.route_path("logs.chapter", log_id=context.log_id, number=context.number))


@view_config(route_name="logs.chapter.message", request_method="GET", renderer="logs/message.mako")
def logs_chapter_message_get(context, request):
    if request.user != context.creator:
        raise HTTPNotFound

    try:
        return {"message_revision": (
            request.db.query(MessageRevision)
            .select_from(ChapterRevisionMessageRevision)
            .join(ChapterRevisionMessageRevision.message_revision)
            # TODO join messages
            .filter(and_(
                ChapterRevisionMessageRevision.chapter_revision_id == context.latest_revision.id,
                MessageRevision.message_id == int(request.matchdict.get("message_id")),
            )).one()
        )}
    except (ValueError, NoResultFound):
        raise HTTPNotFound


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

