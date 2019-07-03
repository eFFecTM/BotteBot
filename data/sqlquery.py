import sqlite3


class SQL_query:
    def __init__(self, db_name):
        # Connect to the SQL database
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

    """Make a convenience function for running SQL queries: SELECT, DELETE, INSERT and UPDATE"""
    def sql_query(self, query):
        cur = self.conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        return rows

    def sql_edit_insert(self, query, var):
        cur = self.conn.cursor()
        cur.execute(query, var)
        self.conn.commit()

    def sql_delete(self, query, var):
        cur = self.conn.cursor()
        cur.execute(query, var)
        self.conn.commit()

    def sql_query2(self, query, var):
        cur = self.conn.cursor()
        cur.execute(query, var)
        rows = cur.fetchall()
        return rows

    """Convert SQL data rows into a dict of JSON data"""
    def sql_db_to_list(self, query):
        self.conn.row_factory = self.list_factory
        cur = self.conn.cursor()
        cur.execute(query)
        results = cur.fetchall()
        return results

    def list_factory(self, cur, row):
        d = []
        for idx, col in enumerate(cur.description):
            d.append(row[idx])
        return d



