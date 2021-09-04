"""Pager class."""
# pylint: disable=too-many-instance-attributes


class Pager():
    """Pager is support class for web/api elements paging."""
    def __init__(self, offset=0, limit=10, order='', sort='asc'):
        self.d_offset = offset
        self.d_limit = limit
        self.d_order = order
        self.d_sort = sort

        self.offset = offset
        self.limit = limit
        self.order = order
        self.sort = sort
        self.total = 0

        self.params = ''

    def bind(self, form):
        """Read and fill attributes from request query arguments."""
        self.offset = form.getfirst("offset", self.offset, int)
        self.limit = form.getfirst("limit", self.limit, int)
        self.order = form.getfirst("order", self.order, str)

        sort = form.getfirst("sort", self.sort, str)
        self.sort = sort if sort in ('asc', 'desc') else self.sort

    def set_params(self, **kwargs):
        """Set params defined by kwargs."""
        self.params = '&'.join('%s=%s' % (key, val)
                               for key, val in kwargs.items())

    @property
    def page(self):
        """Return current page."""
        return int(self.offset / self.limit)

    @property
    def pages(self):
        """Return count of pages."""
        return int((self.total - 1) / self.limit)

    def to_json(self):
        """Return dictionary representation of class for API output."""
        return {
            "offset": self.offset,
            "limit": self.limit,
            "pages": self.pages,
            "page": self.page
        }
