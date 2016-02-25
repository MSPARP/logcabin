import datetime

from bcrypt import gensalt, hashpw
from sqlalchemy import (
    func,
    CheckConstraint,
    Column,
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
    scoped_session,
    sessionmaker,
)
from zope.sqlalchemy import ZopeTransactionExtension

from logcabin.models.types import URLSegment, EmailAddress

Session = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class User(Base):
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

