"""Init file for module use in uwsgi."""
from . lib.core import app

# another way how to call: from . main import *, but pep8 OK
__import__('lib.openapi', globals=globals(), level=1)
__import__('page', globals=globals(), level=1)
__import__('parts', globals=globals(), level=1)
__import__('categories', globals=globals(), level=1)
__import__('update', globals=globals(), level=1)

__all__ = ["app"]
