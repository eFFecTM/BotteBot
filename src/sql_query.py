import sqlite3


class SqlQuery:
    """Contains convenience functions for running SQL queries: SELECT, DELETE, INSERT and UPDATE"""

    def __init__(self, db_name):
        # Connect to the SQL database
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.conn.row_factory = list_factory

    def sql_get(self, query, var=None):
        """Getting any information from database using SELECT statements"""
        cur = self.conn.cursor()
        if var:
            cur.execute(query, var)
        else:
            cur.execute(query)
        results = cur.fetchall()
        return results

    def sql_set(self, query, var=None):
        """Setting any information in database using DELETE, INSERT, UPDATE statements"""
        cur = self.conn.cursor()
        if var:
            cur.execute(query, var)
        else:
            cur.execute(query)
        self.conn.commit()


def list_factory(cur, row):
    """ Allows conversion of SQL data rows into a list of data"""
    d = []
    for idx, col in enumerate(cur.description):
        d.append(row[idx])
    return d


database = SqlQuery('data/imaginelab.db')
