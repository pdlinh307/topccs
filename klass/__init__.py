from klass.appconfig import AppConfig
from klass.database import MySQLConnector
from klass.asterisk import AsteriskAMI
from apscheduler.schedulers.background import BackgroundScheduler

conf = AppConfig(file='config/app.conf')
db = MySQLConnector(option_files='config/mysql.conf')
ami = AsteriskAMI(config=conf.section(name='asterisk'))

scheduler = BackgroundScheduler()
scheduler.add_jobstore('redis', jobs_key='wk.jobs', run_times_key='wk.run_times')
scheduler.start()
