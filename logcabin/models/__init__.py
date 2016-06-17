import datetime
import markdown

from bcrypt import gensalt, hashpw
from markupsafe import Markup, escape
from pyramid.decorator import reify
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
    UnicodeText,
)
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    relationship,
    sessionmaker,
)
from zope.sqlalchemy import ZopeTransactionExtension

from logcabin.models.types import URLSegment, EmailAddress
from logcabin.lib.formats import camel_registry


md = markdown.Markdown()


Session = sessionmaker(extension=ZopeTransactionExtension())
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
    created = Column(DateTime, nullable=False, server_default=func.now())
    last_online = Column(DateTime, nullable=False, server_default=func.now())
    last_ip = Column(INET, nullable=False)
    status = Column(Enum("guest", "active", "banned", name="user_status"), nullable=False, default=u"active")
    is_admin = Column(Boolean, nullable=False, default=False)
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

    def __json__(self, request=None):
        return {
            "id": self.id,
            "username": self.username,
        }

    def set_password(self, password):
        if not password:
            raise ValueError("Password can't be blank.")
        self.password = hashpw(password.encode("utf8"), gensalt()).decode()

    def check_password(self, password):
        if not self.password:
            return False
        return hashpw(password.encode("utf8"), self.password.encode()) == self.password.encode()


camel_registry.dumper(User, "user", version=None)(User.__json__)

Index("users_username", func.lower(User.username), unique=True)
Index("users_email_address", func.lower(User.email_address), unique=True)


class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(100), nullable=False)
    creator_id = Column(Integer, ForeignKey(User.id), nullable=False)
    created = Column(DateTime, nullable=False, server_default=func.now())
    last_modified = Column(DateTime, nullable=False, server_default=func.now())
    summary = Column(Unicode(255))

    def __repr__(self):
        return "<Log #{}: {}>".format(self.id, self.name)

    def __json__(self, request=None):
        return {
            "id": self.id,
            "name": self.name,
            "creator": self.creator,
            "created": self.created,
            "last_modified": self.last_modified,
            "summary": self.summary,
        }

camel_registry.dumper(Log, "log", version=None)(Log.__json__)

Log.creator = relationship(User, backref="logs_created")


class Source(Base):
    __tablename__ = "sources"
    __mapper_args__ = {"polymorphic_on": "type"}
    id = Column(Integer, primary_key=True)
    log_id = Column(Integer, ForeignKey(Log.id), nullable=False)
    type = Column(Enum("cherubplay", "msparp", name="source_type"), nullable=False)
    url = Column(Unicode(100), nullable=False)
    account_id = Column(Integer, nullable=False)
    last_import = Column(DateTime, nullable=False, server_default=func.now())
    auto_import = Column(Boolean, nullable=False, server_default="true")

Source.log = relationship(Log, backref="sources")


class CherubplaySource(Source):
    __mapper_args__ = {"polymorphic_identity": "cherubplay"}


class MSPARPSource(Source):
    __mapper_args__ = {"polymorphic_identity": "msparp"}


class Chapter(Base):
    __tablename__ = "chapters"
    id = Column(Integer, primary_key=True)
    log_id = Column(Integer, ForeignKey(Log.id), nullable=False)
    number = Column(Integer, nullable=False)
    name = Column(Unicode(100), nullable=False)
    creator_id = Column(Integer, ForeignKey(User.id), nullable=False)
    created = Column(DateTime, nullable=False, server_default=func.now())
    last_modified = Column(DateTime, nullable=False, server_default=func.now())

    def __repr__(self):
        return "<Chapter #{}: {}>".format(self.id, self.name)

    def __json__(self, request=None):
        return {
            "id": self.id,
            "number": self.number,
            "name": self.name,
            "creator": self.creator,
            "created": self.created,
            "last_modified": self.last_modified,
        }

camel_registry.dumper(Chapter, "chapter", version=None)(Chapter.__json__)

Chapter.log = relationship(Log, backref="chapters")
Chapter.creator = relationship(User, backref="chapters_created")


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    chapter_id = Column(Integer, ForeignKey(Chapter.id), nullable=False)
    number = Column(Integer, nullable=False)
    creator_id = Column(Integer, ForeignKey(User.id), nullable=False)
    created = Column(DateTime, nullable=False, server_default=func.now())
    last_modified = Column(DateTime, nullable=False, server_default=func.now())
    text = Column(UnicodeText, nullable=False)

    @reify
    def html(self):
        return Markup(md.convert(escape(self.text)))

    def __repr__(self):
        if len(self.text) > 50:
            return "<Message #{}: {}>".format(self.id, self.text[:47] + "...")
        return "<Message #{}: {}>".format(self.id, self.text)

    def __json__(self, request=None):
        return {
            "id": self.id,
            "number": self.number,
            "creator": self.creator,
            "created": self.created,
            "last_modified": self.last_modified,
            "text": self.text,
        }

camel_registry.dumper(Message, "message", version=None)(Message.__json__)

Message.chapter = relationship(Chapter, backref="messages")
Message.creator = relationship(User, backref="messages_created")


class LogSubscription(Base):
    __tablename__ = "log_subscriptions"
    user_id = Column(Integer, ForeignKey(User.id), primary_key=True)
    log_id = Column(Integer, ForeignKey(Log.id), primary_key=True)
    created = Column(DateTime, nullable=False, server_default=func.now())

    def __json__(self, request=None):
        return {
            "user": self.user,
            "log": self.log,
            "created": self.created,
        }

camel_registry.dumper(LogSubscription, "log_subscription", version=None)(LogSubscription.__json__)

LogSubscription.user = relationship(User, backref="log_subscriptions")
LogSubscription.log = relationship(Log, backref="subscribers")


class Favorite(Base):
    __tablename__ = "favorites"
    user_id = Column(Integer, ForeignKey(User.id), primary_key=True)
    log_id = Column(Integer, ForeignKey(Log.id), primary_key=True)
    created = Column(DateTime, nullable=False, server_default=func.now())

    def __json__(self, request=None):
        return {
            "user": self.user,
            "log": self.log,
            "created": self.created,
        }

camel_registry.dumper(Favorite, "favorite", version=None)(Favorite.__json__)

Favorite.user = relationship(User, backref="favorites")
Favorite.log = relationship(Log, backref="favorites")

