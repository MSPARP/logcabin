import datetime

from sqlalchemy import (
    func,
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

Session = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(Unicode(50), nullable=False) # Gotta be alphanumeric
    password = Column(String(60), nullable=False) # bcrypt hash
    created = Column(DateTime, nullable=False, default=datetime.datetime.now)
    last_online = Column(DateTime, nullable=False, default=datetime.datetime.now)
    last_ip = Column(INET, nullable=False)
    status = Column(Enum("guest", "active", "banned", name="user_status"), nullable=False, default=u"active")
    unban_date = Column(DateTime)
    email_address = Column(Unicode(255), nullable=False)
    email_verified = Column(Boolean, nullable=False, default=False)
    timezone = Column(Unicode(255), nullable=False, default="UTC")

    def __repr__(self):
        return "<User #{}: {}>".format(self.id, self.username)


Index("users_username", func.lower(User.username), unique=True)
Index("users_email_address", func.lower(User.email_address), unique=True)

