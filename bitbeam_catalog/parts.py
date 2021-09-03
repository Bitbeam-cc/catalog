"""Endpoints which work with parts."""
from poorwsgi.response import JSONResponse

from .lib.core import app
from .lib.pager import Pager
from .models.parts import Part


@app.route('/api/parts')
def parts(req):
    """List of printers."""
    category = req.args.getfirst("category")
    pager = Pager(limit=12)
    pager.bind(req.args)

    return JSONResponse(parts=Part.list(pager, category=category),
                        pager=pager.to_json())
    # TODO: JSONGenerator... muhehe


@app.route('/api/parts/<part>')
def part(req, part):
    """Part detail."""
    return JSONResponse(part={})
