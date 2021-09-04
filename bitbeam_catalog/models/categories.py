"""Model definition for categories."""
from sqlite3 import connect

from ..lib.core import app


class Category(dict):
    """Category model definition."""
    @staticmethod
    def list():
        """Return list of categories from DB."""
        with connect(app.cfg.db_uri) as con:
            cur = con.cursor()
            cur.execute(
                """SELECT category, quantity FROM categories
                    WHERE quantity > 0 ORDER BY category
                """)
            for row in cur:
                yield Category(name=row[0], quantity=row[1])
