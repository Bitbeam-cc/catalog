"""Endpoints which work with parts."""
from urllib.request import urlopen
from json import loads
from distutils.version import StrictVersion
from zipfile import ZipFile
from os import symlink, unlink
from os.path import lexists
from shutil import rmtree

import logging

from poorwsgi import state
from poorwsgi.response import EmptyResponse
from uwsgidecorators import timer

import uwsgi

from . lib.core import app

URL = "https://api.github.com/repos/ondratu/m-bitbeam/releases/latest"
log = logging.getLogger(__name__)


@app.route('/api/parts', method=state.METHOD_PUT)
def parts(req):
    """List of printers."""
    state = (uwsgi.queue_get(0) or b"\0")[0]
    state |= (1 << 0)   # first byte means do update
    uwsgi.queue_set(0, bytes([state]))
    return EmptyResponse()


def download(tag, name, url):
    log.info(f"Download {url}")
    res = urlopen(url)
    zip_path = app.cfg.static_files+"/data/"+name
    with open(zip_path, "wb+") as zipfile:
        zipfile.write(res.read())

    log.info(f"Extract files from {name}")
    with ZipFile(zip_path) as zipfile:
        zipfile.extractall(app.cfg.static_files+f"/data/{tag}/")
    return


@timer(10)
def check_update(num):
    state = (uwsgi.queue_get(0) or b"\0")[0]
    if not state & (1 << 0):
        return      # update bit not set
    if state & (1 << 1):
        return      # running bit is set

    state = (1 << 1)   # not update but running
    uwsgi.queue_set(0, bytes([state]))

    try:
        log.info("Check new release")
        res = urlopen(URL)
        data = loads(res.read())
        tag = data["tag_name"]
        old_version = app.cfg.db_version
        if StrictVersion(tag) > StrictVersion(old_version):
            log.info(f"New version {tag} found")

            for asset in data["assets"]:
                name = asset["name"]
                if name.startswith("m-bitbeam-catalog"):
                    download(tag, name, asset["browser_download_url"])
                elif name.startswith("m-bitbeam-stl"):
                    download(tag, name, asset["browser_download_url"])
                else:
                    log.debug(f"skip {name}")

            log.info(f"Creating symlinks")
            data_path = app.cfg.static_files+"/data"
            for it in ("stl", "png", "catalog.db"):
                if lexists(f"{data_path}/{it}"):
                    unlink(f"{data_path}/{it}")
                symlink(f"{tag}/{it}", f"{data_path}/{it}")

            log.info(f"Removing old version {old_version}")
            if lexists(f"{data_path}/{old_version}"):
                rmtree(f"{data_path}/{old_version}")

            log.info("Update is done")
    except Exception:
        log.exception("Check failed")
    finally:
        state = (uwsgi.queue_get(0) or b"\0")[0]
        state = state & ~ (1 << 1)   # clean running bit
        uwsgi.queue_set(0, bytes([state]))
