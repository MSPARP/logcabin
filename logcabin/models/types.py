import re

from sqlalchemy.types import TypeDecorator, Unicode


class RegexValidatedType(TypeDecorator):
    def process_bind_param(self, value, dialect):
        if value and not self.regex.match(value):
            raise ValueError("value must match the regex {}".format(self.regex.pattern))
        return value


class URLSegment(RegexValidatedType):
    impl = Unicode(50)
    regex = re.compile("^[-a-zA-Z0-9_]+$")


class EmailAddress(RegexValidatedType):
    impl = Unicode(255)
    regex = re.compile("^.+@.+\..+$")


class Color(RegexValidatedType): # TODO force lower case
    impl = Unicode(6)
    regex = re.compile("^[A-Fa-f0-9]{6}$")

    def process_bind_param(self, value, dialect):
        if value:
            value = value.lower()
        return super().process_bind_param(value, dialect)

