from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy.orm.exc import NoResultFound

from logcabin.models import Session, User


def get_user(request):
    try:
        return Session.query(User).filter(User.username == request.matchdict["username"]).one()
    except NoResultFound:
        raise HTTPNotFound
