import sqlite3
import logging
import utils

logger = logging.getLogger('bot')


class Database:
    def __init__(
            self,
            db_path: str
    ):
        self._con = sqlite3.connect(db_path)
        self._pragma()

    def _pragma(self):
        cur = self._con.cursor()
        try:
            cur.execute('PRAGMA foreign_keys = on')
        except sqlite3.Error as e:
            logger.error(e)
        else:
            self._con.commit()
        finally:
            cur.close()

    def _insert_into(self, table_name, **kwargs) -> bool:
        cursor = self._con.cursor()
        keys = []
        values = []
        for key, value in kwargs.items():
            keys.append(key)
            values.append(value)
        query = f'''insert into {table_name} ({",".join(keys)}) VALUES ({",".join(['?' for i in range(len(keys))])})'''
        try:
            cursor.execute(query,
                           tuple(values))
        except sqlite3.Error as e:
            logger.error(e)
            return False
        finally:
            self._con.commit()
            cursor.close()
        return True

    def _select(self, table_name: str, columns=None, fetchone=False, **kwargs):
        if columns is None:
            columns = []
        cursor = self._con.cursor()
        keys = []
        values = []
        for key, value in kwargs.items():
            keys.append(f"{key} = ?")
            values.append(value)
        query = f'''select {",".join(columns) if len(columns) > 0 else "*"} from {table_name} ''' + f'''{f"where {' and '.join(keys)}" if len(keys) > 0 else ''}'''
        try:
            cursor.execute(query, tuple(values))
        except sqlite3.Error as e:
            logger.error(e)
            return False
        else:
            if fetchone:
                return cursor.fetchone()
            else:
                return cursor.fetchall()
        finally:
            cursor.close()

    def _delete(self, table_name: str, **kwargs) -> bool:
        cursor = self._con.cursor()
        keys = []
        values = []
        for key, value in kwargs.items():
            keys.append(f"{key} = ?")
            values.append(value)
        query = f'''delete from {table_name} where {" and ".join(keys)}'''
        try:
            cursor.execute(query, tuple(values))
        except sqlite3.Error as e:
            logger.error(e)
            return False
        else:
            self._con.commit()
        finally:
            cursor.close()
        return True

    def _update(self, table_name, columns: dict, **kwargs) -> bool:
        cursor = self._con.cursor()
        keys = []
        values = []
        where_keys = []
        where_values = []
        for key, value in columns.items():
            keys.append(f'{key} = ?')
            values.append(value)
        for key, value in kwargs.items():
            where_values.append(value)
            where_keys.append(f'{key} = ?')
        try:
            query = f'''update {table_name} set {",".join(keys)} ''' + f'''{f"where {' and '.join(where_keys)}" if len(where_keys) > 0 else ''}'''
            cursor.execute(query, tuple(values + where_values))
        except sqlite3.Error as e:
            logger.error(e)
            return False
        else:
            self._con.commit()
        finally:
            cursor.close()
        return True

    def _check(self, table_name, **kwargs):
        cursor = self._con.cursor()
        keys = []
        values = []
        for key, value in kwargs.items():
            keys.append(f"{key} = ?")
            values.append(value)
        where = " and ".join(keys)
        query = f'select count(*) from "{table_name}" where {where}'
        try:
            cursor.execute(query, tuple(values))
        except sqlite3.Error as e:
            logger.error(e)
            raise e
        else:
            data = cursor.fetchone()[0]
        finally:
            cursor.close()
        return data > 0


class Users(Database):
    table_name = 'Users'

    def add(self, telegram_id, first_name, last_name):
        if self._check(table_name=self.table_name, id=telegram_id):
            return False
        return self._insert_into(table_name=self.table_name, id=telegram_id, first_name=first_name, last_name=last_name,
                                 date=utils.time())

    def delete(self, telegram_id):
        self._delete(table_name=self.table_name, id=telegram_id)


class Events(Database):
    table_name = 'events'

    def add(self, telegram_id, filename):
        return self._insert_into(table_name=self.table_name, user_id=telegram_id, filename=filename, time=utils.time())
