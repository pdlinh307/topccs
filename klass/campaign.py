# -*- coding: utf-8 -*-
from datetime import datetime
from klass.exceptions import CampaignError, DBError
from klass.singleton import Singleton
from klass import db


class Campaign(metaclass=Singleton):
    __config = None

    def __init__(self, config):
        self.__config = config

    def insert(self, data):
        # Check payload
        required_fields = self.__config['required_fields_campaign'].split(',')
        if data is None:
            raise CampaignError('PAYLOAD_EMPTY')
        for f in required_fields:
            if f not in data:
                raise CampaignError('PARAM_MISS')

        cid = int(data['campaignid'])

        # Check unique id
        if self.select_one(table='cdr', where=dict(campaign_id=cid)):
            raise CampaignError('ID_EXISTED')

        # Parse datetime
        try:
            fmt = self.__config['datetime_format']
            time_start = datetime.strptime(data['starttime'], fmt)
            time_end = datetime.strptime(data['endtime'], fmt)
            if time_end < time_start or time_end < datetime.now():
                raise CampaignError('PARAM_INVALID')
        except ValueError:
            raise CampaignError('DATETIME_FORMAT')

        # Insert
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO `campaigns`(`campaign_id`, `time_start`, `time_end`)"
                           "VALUES (%s, %s, %s)", (cid, time_start, time_end))
            if cursor.rowcount == 1:
                cts = list(filter(lambda c: self.__config['required_field_contacts'] in c, data['contact']))
                cts = list(map(lambda c: (cid, int(c['id']), c['phonenumber'], c.get('linkedit', None)), cts))
                cursor.executemany("INSERT INTO `cdr`(`campaign_id`, `contact_id`, `phone_number`, `linkedit`)"
                                   "VALUES (%s, %s, %s, %s)", cts)
                return cursor.rowcount
        except:
            raise DBError('ERROR')
        finally:
            cursor.close()

    @staticmethod
    def select_one(table, where):
        wherestr = ' AND '.join(list(map(lambda k: "{0} = %({0})s".format(k), where.keys())))
        query = "SELECT * FROM {0} WHERE {1} LIMIT 1".format(table, wherestr)
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(query)
            return cursor.fetchone()
        except:
            raise DBError('ERROR')
        finally:
            cursor.close()

    @staticmethod
    def select_many(table, where):
        wherestr = ' AND '.join(list(map(lambda k: "{0} = %({0})s".format(k), where.keys())))
        query = "SELECT * FROM {0} WHERE {1}".format(table, wherestr)
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(query)
            return cursor.fetchall()
        except:
            raise DBError('ERROR')
        finally:
            cursor.close()

    @staticmethod
    def update(table, where, data):
        wherestr = ' AND '.join(list(map(lambda w: "{0} = %({0})s", where)))
        keys = list(filter(lambda u: u not in where, data.keys()))
        setstr = ', '.join(list(map(lambda k: "{0} = %({0})s".format(k), keys)))
        query = "UPDATE {0} SET {1} WHERE {2}".format(table, setstr, wherestr)
        cursor = db.cursor()
        try:
            cursor.execute(query, data)
            return cursor.rowcount
        except:
            raise DBError('ERROR')
        finally:
            cursor.close()
