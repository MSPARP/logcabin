from pyramid.view import view_config
from sqlalchemy import func
from sqlalchemy.orm import joinedload

from logcabin.models import Chapter, Log, Message


@view_config(route_name="logs.log", renderer="logs/log.mako")
@view_config(route_name="logs.log.ext", extension="json", renderer="json")
@view_config(route_name="logs.log.ext", extension="yaml", renderer="yaml")
def logs_log(context, request):
    chapter_count = request.db.query(func.count("*")).select_from(Chapter).filter(Chapter.log_id == context.id).scalar()
    if chapter_count <= 10:
        oldest_chapters = request.db.query(Chapter).filter(Chapter.log_id == context.id).order_by(Chapter.number).all()
        newest_chapters = []
    else:
        oldest_chapters = request.db.query(Chapter).filter(Chapter.log_id == context.id).order_by(Chapter.number).limit(5).all()
        newest_chapters = request.db.query(Chapter).filter(Chapter.log_id == context.id).order_by(Chapter.number.desc()).limit(5).all()
        newest_chapters.reverse()
    return {
        "log": context,
        "chapter_count": chapter_count,
        "oldest_chapters": oldest_chapters,
        "newest_chapters": newest_chapters,
    }


@view_config(route_name="logs.chapters", renderer="logs/chapters.mako")
@view_config(route_name="logs.chapters.ext", extension="json", renderer="json")
@view_config(route_name="logs.chapters.ext", extension="yaml", renderer="yaml")
def logs_chapters(context, request):
    return {"chapters": request.db.query(Chapter).filter(Chapter.log_id == context.id).order_by(Chapter.number).all()}


@view_config(route_name="logs.chapter", renderer="logs/chapter.mako")
@view_config(route_name="logs.chapter.ext", extension="json", renderer="json")
@view_config(route_name="logs.chapter.ext", extension="yaml", renderer="yaml")
def logs_chapter(context, request):
    return {
        "chapter": context,
        "messages": request.db.query(Message).filter(Message.chapter_id == context.id).order_by(Message.number).all(),
    }

