from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy import and_
from sqlalchemy.exc import StatementError
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound

from logcabin.models import User, Log, Chapter


def get_user(request):
    try:
        return request.db.query(User).filter(User.username == request.matchdict["username"]).one()
    except (NoResultFound, StatementError):
        raise HTTPNotFound


def get_log(request):
    try:
        log = request.db.query(Log).filter(Log.id == int(request.matchdict["log_id"])).one()
    except (ValueError, NoResultFound):
        raise HTTPNotFound
    request.response.headers["Last-Modified"] = log.last_modified.strftime("%a, %d %b %Y %H:%M:%S UTC")
    return log


def get_chapter(request):
    try:
        chapter = request.db.query(Chapter).filter(and_(
            Chapter.log_id == int(request.matchdict["log_id"]),
            Chapter.number == int(request.matchdict["number"]),
        )).options(joinedload(Chapter.log)).one()
    except (ValueError, NoResultFound):
        raise HTTPNotFound
    request.response.headers["Last-Modified"] = chapter.last_modified.strftime("%a, %d %b %Y %H:%M:%S UTC")
    return chapter

