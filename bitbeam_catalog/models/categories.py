from sqlite3 import connect

from .. lib.core import app


class Category:
    @staticmethod
    def list():
        with connect(app.cfg.db_uri) as con:
            cur = con.cursor()
            cur.execute(
                """SELECT category FROM categories
                    WHERE category != 'Support' ORDER BY category
                """)
            return cur.fetchall()
