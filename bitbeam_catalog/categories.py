"""Endpoints which work with categories."""
from poorwsgi.response import JSONResponse

from . lib.core import app
from . models.categories import Category


@app.route('/api/categories')
def categories(req):
    """List of categories"""
    return JSONResponse(
        categories=list(Category.list())
    )
