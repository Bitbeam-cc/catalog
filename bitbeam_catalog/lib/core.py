"""Core application instance."""
import os

from poorwsgi import Application

from .. import __name__ as appname
from .config import Config

if "CONFFILE" not in os.environ:
    raise RuntimeError("CONFFILE env variable not defined!")

app = application = Application(appname)
app.debug = True
app.keep_blank_values = 1
app.cfg = Config(os.environ["CONFFILE"])
app.document_root = app.cfg.static_files + "/web"
