import mysql.connector
from klass.exceptions import DBError


class MySQLConnector(object):
    __instance = None
    __cnx = None
    __option_file = None

    @staticmethod
    def get_instance(option_file):
        """ Static access method """
        if MySQLConnector.__instance is None:
            MySQLConnector(option_file=option_file)
        return MySQLConnector.__instance

    def __init__(self, option_file):
        """ Private constructor """
        if MySQLConnector.__instance is not None:
            raise DBError('DB_SINGLETON_CLASS')
        MySQLConnector.__instance = self
        self.__option_file = option_file
        self._db_connect()

    def __del__(self):
        self.__cnx.close()

    def _db_connect(self):
        try:
            self.__cnx = mysql.connector.connect(option_files=self.__option_file)
        except:
            raise DBError('DB_CONNECT_ERROR')

    def get_cursor(self, **kwargs):
        return self.__cnx.cursor(**kwargs)