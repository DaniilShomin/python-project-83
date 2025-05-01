from psycopg2.extras import DictCursor


class UrlReposetory:
    def __init__(self, conn):
        self.conn = conn
    
    def get_content(self, reversed=False):
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            if reversed:
                cur.execute("SELECT * FROM urls ORDER BY id DESC")
            else:
                cur.execute("SELECT * FROM urls")
            return [dict(row) for row in cur]
        
    def find(self, id):
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT * FROM urls WHERE id = %s", (id,))
            row = cur.fetchone()
            return dict(row) if row else None
        
    def save(self, url):
        if "id" in url and url["id"]:
            self._update(url)
        else:
            self._create(url)

    def _update(self, url):
        with self.conn.cursor() as cur:
            cur.execute(
                "UPDATE urls SET name = %s, created_at = %s WHERE id = %s",
                (url['name'], url['created_at'], url["id"]),
            )
        self.conn.commit()

    def _create(self, url):
        with self.conn.cursor() as cur:
            cur.execute(
                """INSERT INTO urls (name, created_at) 
                VALUES (%s, %s) RETURNING id""",
                (url['name'], url['created_at']),
            )
            id = cur.fetchone()[0]
            url['id'] = id
        self.conn.commit()

    def get_by_name(self, name):
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT * FROM urls WHERE name = %s", (name,))
            row = cur.fetchone()
            return dict(row) if row else None
        

class UrlCheckReposetory:
    def __init__(self, conn):
        self.conn = conn

    def get_add(self, data):
        with self.conn.cursor() as cur:
            cur.execute(
                """INSERT INTO url_checks 
                (url_id, status_code, h1, title, description, created_at) 
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id""",
                (data['url_id'], 
                 data['status_code'], 
                 data['h1'], 
                 data['title'], 
                 data['description'], 
                 data['created_at']),
            )
            id = cur.fetchone()[0]
            data['id'] = id
        self.conn.commit()

    def get_content(self, id, reversed=False):
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            if reversed:
                cur.execute(
                    """SELECT * FROM url_checks 
                    WHERE url_id = %s ORDER BY id DESC""", 
                    (id,)
                )
            else:
                cur.execute("SELECT * FROM url_checks WHERE url_id = %s", (id,))
            return [dict(row) for row in cur]
        
    def find_last_check(self, id):
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(
                """SELECT * FROM url_checks 
                WHERE url_id = %s ORDER BY id DESC""", 
                (id,)
            )
            row = cur.fetchone()
            return dict(row) if row else {}