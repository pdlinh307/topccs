from klass.appconfig import AppConfig
from klass.database import MySQLConnector

conf = AppConfig.get_instance(filepath='config/campaign.conf')
db = MySQLConnector.get_instance(option_file='config/mysql.conf')
