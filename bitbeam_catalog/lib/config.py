"""Configuration module."""
import logging as log
from os.path import abspath, join
from sqlite3 import OperationalError, connect

from extendparser import ExtendParser
from openapi_core import create_spec
from openapi_core.shortcuts import RequestValidator, ResponseValidator
from openapi_spec_validator.schemas import read_yaml_file

from .. import __name__ as appname

HANDLER = log.StreamHandler()
log.root.addHandler(HANDLER)
log.getLogger("poorwsgi").setLevel("WARNING")
log.getLogger("openapi_spec_validator.validators").setLevel("WARNING")
log.getLogger("openapi_spec_validator.decorators").setLevel("WARNING")
log.getLogger("parse").setLevel("INFO")

LOGGER = log.getLogger(appname)

LOG_FORMAT = ("%(asctime)s %(levelname)s: %(name)s: %(message)s "
              "{%(filename)s.%(funcName)s():%(lineno)d}")

OPEN_API = "openapi.yaml"

# pylint: disable=too-many-ancestors

class Config(ExtendParser):
    """Configuration class."""
    def __init__(self, config_file):
        super().__init__()

        with open(config_file, "r") as src:
            self.read_file(src)

        self.log_level = self.get_option("logging",
                                         "level",
                                         fallback="WARNING")
        self.log_format = self.get_option("logging",
                                          "format",
                                          fallback=LOG_FORMAT)

        log.root.setLevel(self.log_level)  # final output
        LOGGER.setLevel(self.log_level)
        HANDLER.setFormatter(log.Formatter(self.log_format))

        self.static_files = abspath(self.get_option("main", "static_files"))

        self.validate_response = self.get_option("main",
                                                 "validate_response",
                                                 target=bool,
                                                 fallback=False)
        spec = create_spec(read_yaml_file(join(self.static_files, OPEN_API)))
        self.request_validator = RequestValidator(spec)
        self.response_validator = ResponseValidator(spec)

        self.db_uri = self.get_option("main", "db_uri").format(**self.__dict__)
        log.info(f"DB uri: {self.db_uri}")
        self.db_version  # just check the version at start

    @property
    def db_version(self):
        """Return DB version read from DB file."""
        try:
            with connect(self.db_uri, uri=True) as db:
                cur = db.cursor()
                cur.execute("SELECT version FROM release")
                return cur.fetchone()[0]
        except OperationalError:
            log.exception("DB Version is 0")
            return "0.0.0"
