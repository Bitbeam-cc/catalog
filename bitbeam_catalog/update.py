"""Endpoints which work with parts."""
import logging
from distutils.version import StrictVersion
from json import loads
from os import symlink, unlink
from os.path import lexists
from shutil import rmtree
from urllib.request import urlopen
from zipfile import ZipFile

import uwsgi  # pylint: disable=import-error
from poorwsgi import state
from poorwsgi.response import EmptyResponse
from uwsgidecorators import timer

from .lib.core import app

URL = "https://api.github.com/repos/m-Bitbeam/m-bitbeam/releases/latest"
log = logging.getLogger(__name__)


@app.route('/api/parts', method=state.METHOD_PUT)
def parts(req):
    """Set internal update flag to check new release."""
    assert req
    state_byte = (uwsgi.queue_get(0) or b"\0")[0]
    state_byte |= (1 << 0)  # first byte means do update
    uwsgi.queue_set(0, bytes([state_byte]))
    return EmptyResponse()


def download(tag, name, url):
    """Process download new m-bitbeam release."""
    log.info("Download %s", url)
    with urlopen(url) as res:
        zip_path = app.cfg.static_files + "/data/" + name
        with open(zip_path, "wb+") as zipfile:
            zipfile.write(res.read())

    log.info("Extract files from %s", name)
    with ZipFile(zip_path) as zipfile:
        zipfile.extractall(app.cfg.static_files + f"/data/{tag}/")


@timer(60)
def check_update(num):
    """Check update flag.

    When flag is set, and no other update process is not run, download
    release info. When release is updated on github, download and use it.
    """
    # pylint: disable=too-many-branches
    assert num
    state_byte = (uwsgi.queue_get(0) or b"\0")[0]
    if not state_byte & (1 << 0):
        return  # update bit not set
    if state_byte & (1 << 1):
        return  # running bit is set

    state_byte = (1 << 1)  # not update but running
    uwsgi.queue_set(0, bytes([state_byte]))

    try:
        log.info("Check new release")
        with urlopen(URL) as res:
            data = loads(res.read())
        tag = data["tag_name"]
        old_version = app.cfg.db_version
        if StrictVersion(tag) > StrictVersion(old_version):
            log.info("New version %s found", tag)

            for asset in data["assets"]:
                name = asset["name"]
                if name.startswith("m-bitbeam-catalog"):
                    download(tag, name, asset["browser_download_url"])
                elif name.startswith("m-bitbeam-stl"):
                    download(tag, name, asset["browser_download_url"])
                else:
                    log.debug("skip %s", name)

            log.info("Creating symlinks")
            data_path = app.cfg.static_files + "/data"
            for obj in ("stl", "png", "catalog.db"):
                if lexists(f"{data_path}/{obj}"):
                    unlink(f"{data_path}/{obj}")
                symlink(f"{tag}/{obj}", f"{data_path}/{obj}")

            log.info("Removing old version %s", old_version)
            if lexists(f"{data_path}/{old_version}"):
                rmtree(f"{data_path}/{old_version}")

            log.info("Update is done")
    except Exception:  # pylint: disable=broad-except
        log.exception("Check failed")
    finally:
        state_byte = (uwsgi.queue_get(0) or b"\0")[0]
        state_byte = state_byte & ~(1 << 1)  # clean running bit
        uwsgi.queue_set(0, bytes([state_byte]))
