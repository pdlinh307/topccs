# -*- coding: utf-8 -*-
import mysql.connector
from klass.exceptions import DBError
from klass.singleton import Singleton


class MySQLConnector(metaclass=Singleton):
    __cnx = None
    __option_files = None

    def __init__(self, option_files):
        self.__option_files = option_files
        self._connect()

    def __del__(self):
        self.__cnx.close()

    def _connect(self):
        try:
            self.__cnx = mysql.connector.connect(option_files=self.__option_files, use_pure=True)
        except:
            raise DBError('CONNECT_ERROR')

    def cursor(self, **kwargs):
        if not self.__cnx.is_connected():
            self._connect()
        return self.__cnx.cursor(**kwargs)

    def rollback(self):
        self.__cnx.rollback()
