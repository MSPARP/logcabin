from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy import and_
from sqlalchemy.exc import StatementError
from sqlalchemy.orm.exc import NoResultFound

from logcabin.models import Session, User, Log, Chapter


def get_user(request):
    try:
        return Session.query(User).filter(User.username == request.matchdict["username"]).one()
    except (NoResultFound, StatementError):
        raise HTTPNotFound


def get_log(request):
    try:
        return Session.query(Log).filter(Log.id == int(request.matchdict["log_id"])).one()
    except (ValueError, NoResultFound):
        raise HTTPNotFound


def get_chapter(request):
    log = get_log(request)
    try:
        return Session.query(Chapter).filter(and_(
            Chapter.log_id == log.id,
            Chapter.number == int(request.matchdict["number"]),
        )).one()
    except (ValueError, NoResultFound):
        raise HTTPNotFound

