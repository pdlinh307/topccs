from klass.appconfig import AppConfig
from klass.database import MySQLConnector

conf = AppConfig(file='config/app.conf')
db = MySQLConnector(option_files='config/mysql.conf')
