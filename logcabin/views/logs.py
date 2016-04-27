from pyramid.view import view_config
from sqlalchemy.orm import joinedload

from logcabin.models import Session, Chapter, Log, Message


@view_config(route_name="logs.log", renderer="logs/log.mako")
@view_config(route_name="logs.log.ext", extension="json", renderer="json")
@view_config(route_name="logs.log.ext", extension="yaml", renderer="yaml")
def logs_log(context, request):
    return {"log": context}


@view_config(route_name="logs.chapters", renderer="logs/chapters.mako")
@view_config(route_name="logs.chapters.ext", extension="json", renderer="json")
@view_config(route_name="logs.chapters.ext", extension="yaml", renderer="yaml")
def logs_chapters(context, request):
    return {"chapters": Session.query(Chapter).filter(Chapter.log_id == context.id).order_by(Chapter.number).all()}


@view_config(route_name="logs.chapter", renderer="logs/chapter.mako")
@view_config(route_name="logs.chapter.ext", extension="json", renderer="json")
@view_config(route_name="logs.chapter.ext", extension="yaml", renderer="yaml")
def logs_chapter(context, request):
    return {
        "chapter": context,
        "messages": Session.query(Message).filter(Message.chapter_id == context.id).order_by(Message.number).all(),
    }

