"""Base url and errors handlers."""
from traceback import format_exc

from poorwsgi import state
from poorwsgi.response import FileResponse, JSONResponse, Response

from .lib.config import LOGGER as log
from .lib.core import app
from .lib.view import generate_page, markdown2html


@app.http_state(state.HTTP_INTERNAL_SERVER_ERROR)
@app.http_state(state.HTTP_SERVICE_UNAVAILABLE)
def internal_server_error(req):
    """500/503 Internal Server Error handler."""
    assert req
    traceback = format_exc()
    log.error(traceback)
    return JSONResponse(status_code=503, error="Service Unavailable")


@app.http_state(403)
def forbidden(req):
    """403 Forbidden handler."""
    assert req
    return JSONResponse(status_code=403, error="Forbidden")


@app.http_state(404)
def page_not_found(req):
    """404 Not Found handler."""
    if req.accept_json:
        return JSONResponse(status_code=404,
                            error="Entity of Endpoint not found")
    return Response(generate_page("not-found.html"))


@app.route('/__fatal__', state.METHOD_DELETE)
def fatal_error(req):
    """For integrity test only"""
    raise RuntimeError("__fatal__ can't be delete")


@app.route('/')
def root(req):
    """Static root html file."""
    assert req
    return Response(generate_page("index.html", version=app.cfg.db_version))


@app.route('/api', state.METHOD_HEAD)
def availability(req):
    """Test url from any monitoring."""
    assert req
    return b''


@app.route('/api', state.METHOD_GET)
def documentation(req):
    """Static redoc html documentation."""
    assert req
    return Response(generate_page("redoc.html"))


@app.route('/api/version')
def version(req):
    """Return API and library version."""
    assert req
    kwargs = {'API': app.cfg.api_version, 'bitbeam': app.cfg.db_version}
    return JSONResponse(**kwargs)


@app.route('/openapi.yaml')
def openapi(req):
    """Static openapi specific documentation."""
    assert req
    return FileResponse(app.cfg.static_files + "/openapi.yaml")
