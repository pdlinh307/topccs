# -*- coding: utf-8 -*-
import mysql.connector
from klass.exceptions import DBError
from klass.singleton import Singleton


class MySQLConnector(metaclass=Singleton):
    __cnx = None
    __option_files = None

    def __init__(self, option_files):
        self.__option_files = option_files
        self.__connect()

    def __del__(self):
        self.__cnx.close()

    def __connect(self):
        try:
            self.__cnx = mysql.connector.connect(option_files=self.__option_files, use_pure=True)
        except:
            raise DBError('CONNECT_ERROR')

    def __cursor(self, **kwargs):
        if not self.__cnx.is_connected():
            self.__cnx.reconnect(attempts=3, delay=5)
        return self.__cnx.cursor(**kwargs)

    def rollback(self):
        self.__cnx.rollback()

    def select_one(self, table, where):
        wherestr = ' AND '.join(list(map(lambda k: "{0} = %({0})s".format(k), where.keys())))
        query = "SELECT * FROM {0} WHERE {1} LIMIT 1".format(table, wherestr)
        cursor = self.__cursor(dictionary=True)
        try:
            cursor.execute(query, where)
            return cursor.fetchone()
        except:
            raise DBError('ERROR')
        finally:
            cursor.close()

    def select_many(self, table, where):
        wherestr = ' AND '.join(list(map(lambda k: "{0} = %({0})s".format(k), where.keys())))
        query = "SELECT * FROM {0} WHERE {1}".format(table, wherestr)
        cursor = self.__cursor(dictionary=True)
        try:
            cursor.execute(query, where)
            return cursor.fetchall()
        except:
            raise DBError('ERROR')
        finally:
            cursor.close()

    def insert_one(self, table, data):
        wherestr = ', '.join(data.keys())
        valuestr = ', '.join(list(map(lambda k: "%({0})s".format(k), data.keys())))
        query = "INSERT INTO {0}({1}) VALUES ({2})".format(table, wherestr, valuestr)
        cursor = self.__cursor()
        try:
            cursor.execute(query, data)
            return cursor.rowcount
        except:
            raise DBError('ERROR')
        finally:
            cursor.close()

    def insert_many(self, table, data):
        wherestr = ', '.join(data[0].keys())
        valuestr = ', '.join(list(map(lambda k: "%({0})s".format(k), data[0].keys())))
        query = "INSERT INTO {0}({1}) VALUES ({2})".format(table, wherestr, valuestr)
        cursor = self.__cursor()
        try:
            cursor.executemany(query, data)
            return cursor.rowcount
        except:
            raise DBError('ERROR')
        finally:
            cursor.close()

    def update(self, table, where, data):
        wherestr = ' AND '.join(list(map(lambda w: "{0} = %({0})s".format(w), where)))
        keys = list(filter(lambda u: u not in where, data.keys()))
        setstr = ', '.join(list(map(lambda k: "{0} = %({0})s".format(k), keys)))
        query = "UPDATE {0} SET {1} WHERE {2}".format(table, setstr, wherestr)
        cursor = self.__cursor()
        try:
            cursor.execute(query, data)
            return cursor.rowcount
        except:
            raise DBError('ERROR')
        finally:
            cursor.close()
