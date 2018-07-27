from klass.appconfig import AppConfig
from klass.database import MySQLConnector
from apscheduler.schedulers.background import BackgroundScheduler

""" Init instances """
conf = AppConfig(file='config/app.conf')
db = MySQLConnector(option_files='config/mysql.conf')

""" Init scheduler """
scheduler = BackgroundScheduler()
scheduler.add_jobstore('redis', jobs_key='wk.jobs',
                       run_times_key='wk.run_times',
                       db=conf.section(name='redis')['scheduler_db'])
scheduler.start()
