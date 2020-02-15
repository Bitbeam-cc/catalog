from sqlite3 import connect, Row

from .. lib.core import app
from .. lib.config import LOGGER as log


class Part(dict):

    @staticmethod
    def list(pager, category=None):
        cond = "WHERE p.file like 'bb-%'"
        if category is not None:
            cond += " AND pc.category=?"
            args = [category]
        else:
            args = []

        items = []
        with connect(app.cfg.db_uri) as con:
            con.set_trace_callback(log.info)
            cur = con.cursor()
            cur.execute(
                f"""SELECT p.name, p.file FROM parts p
                    LEFT JOIN parts_categories pc ON (p.file = pc.part)
                    {cond} GROUP BY p.file ORDER BY p.file
                    LIMIT ?,?
                """, args+[pager.offset, pager.limit])
            for row in cur:
                row = Row(cur, row)
                items.append(Part(**row))

            cur.execute(
                f"""SELECT count(*) FROM parts p
                    LEFT JOIN parts_categories pc ON (p.file = pc.part)
                    {cond}
                """, args)
            pager.total = cur.fetchone()[0]
            print(pager.total)
        return items
