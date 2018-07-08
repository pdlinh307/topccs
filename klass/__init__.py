from klass.appconfig import AppConfig
from klass.database import MySQLConnector
from klass.asterisk import AsteriskAMI
from klass.campaign import Campaign
from apscheduler.schedulers.background import BackgroundScheduler

""" Init instances """
conf = AppConfig(file='config/app.conf')
db = MySQLConnector(option_files='config/mysql.conf')
camp = Campaign(config=conf.section(name='api'))
ami = AsteriskAMI(config=conf.section(name='asterisk'))

""" Init scheduler """
scheduler = BackgroundScheduler()
scheduler.add_jobstore('redis', jobs_key='wk.jobs', run_times_key='wk.run_times', db=2)
scheduler.start()
