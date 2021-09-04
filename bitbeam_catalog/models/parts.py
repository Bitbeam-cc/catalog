"""Model definition for parts and parts_categories."""
from sqlite3 import Row, connect

from ..lib.config import LOGGER as log
from ..lib.core import app


class Part(dict):
    """Parts model definition."""

    @staticmethod
    def list(pager, category=None):
        """Return listo fo parts."""
        cond = "WHERE p.to_print = 1"
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
                """, args + [pager.offset, pager.limit])
            for row in cur:
                row = Row(cur, row)
                items.append(Part(**row))

            cur.execute(
                f"""SELECT count(*) FROM parts p
                    LEFT JOIN parts_categories pc ON (p.file = pc.part)
                    {cond}
                """, args)
            pager.total = cur.fetchone()[0]
        return items
