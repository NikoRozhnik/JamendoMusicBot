import sqlite3


GET_COL_NAMES_TEMPL = "SELECT * FROM {}"
GET_ALL_TEMPL = "SELECT {} FROM {} WHERE user_id = ?"
ADD_ONE_TEMPL = "INSERT OR REPLACE INTO {}({}) VALUES({})"
DEL_ONE_TEMPL = "DELETE FROM {} WHERE user_id = ? and id = ?"
HAS_ONE_TEMPL = "SELECT ID FROM {} WHERE user_id = ? and id = ?"


class DataBaseAPI:
    def __init__(self, db_name):
        self.db_name = db_name
        self.table_col_names = {
            "artists": self._get_column_names("artists"),
            "albums": self._get_column_names("albums"),
            "tracks": self._get_column_names("tracks"),
        }

    def _connect(self):
        return sqlite3.connect(self.db_name)

    def _get_column_names(self, table_name):
        query = GET_COL_NAMES_TEMPL.format(table_name)
        with self._connect() as con:
            cur = con.cursor()
            cur.execute(query)
            res = [descr[0] for descr in cur.description if descr[0] != "user_id"]
            cur.close()
        return res

    def _do_get_all(self, table_name, user_id):
        col_names = self.table_col_names[table_name]
        query = GET_ALL_TEMPL.format(", ".join(col_names), table_name)
        with self._connect() as con:
            res = [dict(zip(col_names, row)) for row in con.execute(query, (user_id,)).fetchall()]
        return res

    def _do_add_one(self, table_name, user_id, item):
        params = {}
        params.update(item)
        params["user_id"] = user_id
        col_names = ["user_id"] + self.table_col_names[table_name]
        p_values = []
        for cn in col_names:
            p_values.append(params[cn])
        query = ADD_ONE_TEMPL.format(table_name, ", ".join(col_names), ", ".join(["?"] * len(col_names)))
        with self._connect() as con:
            con.execute(query, p_values)

    def _do_del_one(self, table_name, user_id, id):
        query = DEL_ONE_TEMPL.format(table_name)
        with self._connect() as con:
            con.execute(query, (user_id, id))

    def _do_has_one(self, table_name, user_id, id):
        query = HAS_ONE_TEMPL.format(table_name)
        with self._connect() as con:
            res = len(con.execute(query, (user_id, id)).fetchall())
        return bool(res)

    def get_fav_artists(self, user_id):
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("'user_id' should be positive integer")
        return self._do_get_all("artists", user_id)

    def get_fav_albums(self, user_id):
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("'user_id' should be positive integer")
        return self._do_get_all("albums", user_id)

    def get_fav_tracks(self, user_id):
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("'user_id' should be positive integer")
        return self._do_get_all("tracks", user_id)

    def add_fav_artist(self, user_id, item):
        self._do_add_one("artists", user_id, item)

    def add_fav_album(self, user_id, item):
        self._do_add_one("albums", user_id, item)

    def add_fav_track(self, user_id, item):
        self._do_add_one("tracks", user_id, item)

    def del_fav_artist(self, user_id, id):
        self._do_del_one("artists", user_id, id)

    def del_fav_album(self, user_id, id):
        self._do_del_one("albums", user_id, id)

    def del_fav_track(self, user_id, id):
        self._do_del_one("tracks", user_id, id)

    def is_fav_artist(self, user_id, id):
        return self._do_has_one("artists", user_id, id)

    def is_fav_album(self, user_id, id):
        return self._do_has_one("albums", user_id, id)

    def is_fav_track(self, user_id, id):
        return self._do_has_one("tracks", user_id, id)
