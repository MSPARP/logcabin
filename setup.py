import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.txt")) as f:
    README = f.read()
with open(os.path.join(here, "CHANGES.txt")) as f:
    CHANGES = f.read()
with open(os.path.join(here, "requirements.txt")) as f:
    requires = f.read().strip().split("\n")

setup(name="logcabin",
      version="0.0",
      description="logcabin",
      long_description=README + "\n\n" + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author="",
      author_email="",
      url="",
      keywords="web wsgi bfg pylons pyramid",
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite="logcabin",
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = logcabin:main
      [console_scripts]
      initialize_logcabin_db = logcabin.scripts.initializedb:main
      """,
      )
