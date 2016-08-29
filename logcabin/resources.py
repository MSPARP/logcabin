from datetime import datetime

from pyramid.httpexceptions import HTTPNotFound, HTTPNotModified
from sqlalchemy import and_
from sqlalchemy.exc import StatementError
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound

from logcabin.models import User, Log, Chapter, FandomCategory, Fandom


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

    request.response.headers["Cache-Control"] = "public;must-revalidate"
    if "If-Modified-Since" in request.headers:
        print(request.headers["If-Modified-Since"])
        if_modified_since = datetime.strptime(request.headers["If-Modified-Since"], "%a, %d %b %Y %H:%M:%S UTC") # TODO make sure this is flexible enough
        if log.last_modified.replace(microsecond=0) <= if_modified_since:
            raise HTTPNotModified

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

    request.response.headers["Cache-Control"] = "public;must-revalidate"
    if "If-Modified-Since" in request.headers:
        print(request.headers["If-Modified-Since"])
        if_modified_since = datetime.strptime(request.headers["If-Modified-Since"], "%a, %d %b %Y %H:%M:%S UTC") # TODO make sure this is flexible enough
        if chapter.latest_revision.created.replace(microsecond=0) <= if_modified_since:
            raise HTTPNotModified

    request.response.headers["Last-Modified"] = chapter.latest_revision.created.strftime("%a, %d %b %Y %H:%M:%S UTC")
    return chapter


def get_fandom_category(request):
    try:
        return request.db.query(FandomCategory).filter(FandomCategory.url_name == request.matchdict["category_url_name"]).one()
    except (NoResultFound, StatementError):
        raise HTTPNotFound


def get_fandom(request):
    category = get_fandom_category(request)
    try:
        return request.db.query(Fandom).filter(and_(
            Fandom.category_id == category.id,
            Fandom.url_name == request.matchdict["fandom_url_name"],
        )).one()
    except (NoResultFound, StatementError):
        raise HTTPNotFound

