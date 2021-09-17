"""Endpoints which work with parts."""
from poorwsgi.response import JSONResponse

from .lib.core import app
from .lib.pager import Pager
from .models.parts import Part


@app.route('/api/parts')
def parts(req):
    """List of print files - kit parts."""
    category = req.args.getfirst("category")
    pager = Pager(limit=12)
    pager.bind(req.args)

    return JSONResponse(parts=Part.list(pager, category=category),
                        pager=pager.to_json())
    # TODO: JSONGenerator... muhehe


@app.route('/api/parts/<file>')
def part_detail(req, file_):
    """Part detail."""
    assert req
    return JSONResponse(**Part.get(file_))
