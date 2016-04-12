import datetime

from bcrypt import gensalt, hashpw
from pyramid.security import Allow, Authenticated, Everyone
from sqlalchemy import (
    func,
    CheckConstraint,
    Column,
    ForeignKey,
    Index,
    Boolean,
    DateTime,
    Enum,
    Integer,
    String,
    Unicode,
)
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    relationship,
    scoped_session,
    sessionmaker,
)
from zope.sqlalchemy import ZopeTransactionExtension

from logcabin.models.types import URLSegment, EmailAddress

Session = scoped_session(sessionmaker(
    extension=ZopeTransactionExtension(),
    expire_on_commit=False,
))
Base = declarative_base()


class Resource(object):
    __acl__ = (
        (Allow, Authenticated, "view"),
        (Allow, "admin", "admin"),
    )


class User(Base, Resource):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("""
            (password IS NOT NULL AND email_address IS NOT NULL AND email_verified IS NOT NULL)
            or
            (password IS NULL AND email_address IS NULL AND email_verified IS NULL)
        """, name="user_password_and_email"),
        CheckConstraint("unban_date IS NOT NULL OR status != 'banned'", name="user_unban_date"),
    )
    id = Column(Integer, primary_key=True)
    username = Column(URLSegment, nullable=False)
    password = Column(String(60)) # bcrypt hash
    created = Column(DateTime, nullable=False, default=datetime.datetime.now)
    last_online = Column(DateTime, nullable=False, default=datetime.datetime.now)
    last_ip = Column(INET, nullable=False)
    status = Column(Enum("guest", "active", "banned", name="user_status"), nullable=False, default=u"active")
    unban_date = Column(DateTime)
    email_address = Column(EmailAddress)
    email_verified = Column(Boolean)
    timezone = Column(Unicode(255), nullable=False, default="UTC")

    @property
    def unban_delta(self):
        if not unban_date:
            return None
        return self.unban_date - datetime.datetime.now()

    def __repr__(self):
        return "<User #{}: {}>".format(self.id, self.username)

    def set_password(self, password):
        if not password:
            raise ValueError("Password can't be blank.")
        self.password = hashpw(password.encode("utf8"), gensalt()).decode()

    def check_password(self, password):
        if not self.password:
            return False
        return hashpw(password.encode("utf8"), self.password.encode()) == self.password.encode()


Index("users_username", func.lower(User.username), unique=True)
Index("users_email_address", func.lower(User.email_address), unique=True)


class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(100), nullable=False)
    creator = Column(Integer, ForeignKey(User.id), nullable=False)
    created = Column(DateTime, nullable=False, default=datetime.datetime.now)
    last_modified = Column(DateTime, nullable=False, default=datetime.datetime.now)

Log.creator = relationship(User, backref="logs_created")


class Chapter(Base):
    __tablename__ = "chapters"
    id = Column(Integer, primary_key=True)
    log_id = Column(Integer, ForeignKey(Log.id), nullable=False)
    number = Column(Integer, nullable=False)
    name = Column(Unicode(100), nullable=False)
    creator = Column(Integer, ForeignKey(User.id), nullable=False)
    created = Column(DateTime, nullable=False, default=datetime.datetime.now)
    last_modified = Column(DateTime, nullable=False, default=datetime.datetime.now)

Chapter.Log = relationship(Log, backref="chapters")
Chapter.creator = relationship(User, backref="chapters_created")


class LogSubscription(Base):
    __tablename__ = "log_subscriptions"
    user_id = Column(Integer, ForeignKey(User.id), primary_key=True)
    log_id = Column(Integer, ForeignKey(Log.id), primary_key=True)
    created = Column(DateTime, nullable=False, default=datetime.datetime.now)

LogSubscription.user = relationship(User, backref="log_subscriptions")
LogSubscription.log = relationship(Log, backref="subscribers")


class Favourite(Base):
    __tablename__ = "favourites"
    user_id = Column(Integer, ForeignKey(User.id), primary_key=True)
    log_id = Column(Integer, ForeignKey(Log.id), primary_key=True)
    created = Column(DateTime, nullable=False, default=datetime.datetime.now)

Favourite.user = relationship(User, backref="favourites")
Favourite.log = relationship(Log, backref="favourites")

