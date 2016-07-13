from pyramid.httpexceptions import HTTPFound
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.view import view_config
from sqlalchemy import and_, func
from sqlalchemy.orm import joinedload

from logcabin.lib.cherubplay import CherubplayClient
from logcabin.models import Chapter, ChapterRevisionMessageRevision, Favorite, Log, Message, MessageRevision


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
        "favorite": request.db.query(Favorite).filter(and_(
            Favorite.log_id == context.id,
            Favorite.user_id == request.user.id,
        )).first() if request.user else None,
    }


@view_config(route_name="logs.chapters", permission=NO_PERMISSION_REQUIRED, renderer="logs/chapters.mako")
@view_config(route_name="logs.chapters.ext", extension="json", permission=NO_PERMISSION_REQUIRED, renderer="json")
@view_config(route_name="logs.chapters.ext", extension="yaml", permission=NO_PERMISSION_REQUIRED, renderer="yaml")
def logs_chapters(context, request):
    return {"chapters": request.db.query(Chapter).filter(Chapter.log_id == context.id).order_by(Chapter.number).all()}


@view_config(route_name="logs.chapter", permission=NO_PERMISSION_REQUIRED, renderer="logs/chapter.mako")
@view_config(route_name="logs.chapter.ext", extension="json", permission=NO_PERMISSION_REQUIRED, renderer="json")
@view_config(route_name="logs.chapter.ext", extension="yaml", permission=NO_PERMISSION_REQUIRED, renderer="yaml")
def logs_chapter(context, request):
    return {"messages": (
        request.db.query(MessageRevision, Message)
        .select_from(ChapterRevisionMessageRevision)
        .join(ChapterRevisionMessageRevision.message_revision)
        .join(MessageRevision.message)
        .order_by(ChapterRevisionMessageRevision.number)
    )}


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

