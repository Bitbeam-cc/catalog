"""Endpoints which work with categories."""
from poorwsgi.response import JSONGeneratorResponse

from .lib.core import app
from .models.categories import Category


@app.route('/api/categories')
def categories(req):
    """List of categories"""
    assert req
    return JSONGeneratorResponse(
        categories=Category.list()
    )
