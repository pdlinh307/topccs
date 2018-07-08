# -*- coding: utf-8 -*-
from datetime import datetime
from klass.exceptions import CampaignError, DBError
from klass.singleton import Singleton
from klass import db


class Campaign(metaclass=Singleton):
    __config = None

    def __init__(self, config):
        self.__config = config

    def cp_check_payload(self, json):
        required_fields = self.__config['cp_required_fields'].split(',')
        if json is None:
            raise CampaignError('CP_INVALID_PAYLOAD')
        for f in required_fields:
            if f not in json:
                raise CampaignError('CP_MISS_PARAM')
        return True

    def cp_check_unique_id(self, campaign_id):
        row = self.cp_select_one(campaign_id)
        if row is not None:
            raise CampaignError('CP_ID_EXISTED')
        return True

    @staticmethod
    def cp_select_one(campaign_id):
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM `campaigns` WHERE `campaign_id` = %s LIMIT 1", (campaign_id,))
            return cursor.fetchone()
        except:
            raise DBError('DB_ERROR')
        finally:
            cursor.close()

    def cp_insert_one(self, json):
        # todo: create schedule job
        try:
            date_format = self.__config['datetime_format']
            time_start = datetime.strptime(json['starttime'], date_format)
            time_end = datetime.strptime(json['endtime'], date_format)
            if time_end < time_start or time_end < datetime.now():
                raise CampaignError('CP_INVALID_PARAM')
        except ValueError:
            raise CampaignError('CP_DATETIME_FORMAT')

        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO `campaigns`(`campaign_id`, `type_id`, `time_start`, `time_end`)"
                           "VALUES (%s, %s, %s, %s)",
                           (int(json['campaignid']), int(json['typeid']), time_start, time_end))
            return cursor.rowcount
        except:
            raise DBError('DB_ERROR')
        finally:
            cursor.close()

    def cp_close_one(self, campaign_id):
        # Todo: cancel all schedule task of this campaign
        row = self.cp_select_one(campaign_id)
        if row is None:
            raise CampaignError('CP_ID_NOT_EXISTED')
        cursor = db.cursor()
        try:
            cursor.execute("UPDATE `campaigns` SET `status_closed` = TRUE "
                           "WHERE `campaign_id` = %s", (campaign_id,))
            return cursor.rowcount
        except Exception:
            raise DBError('DB_ERROR')
        finally:
            cursor.close()

    @staticmethod
    def cp_update(data, where):
        keys = list(filter(lambda u: u not in where, data.keys()))
        sets = ', '.join(list(map(lambda k: "{0} = %({0})s".format(k), keys)))
        cods = ' AND '.join(list(map(lambda w: "{0} = %({0})s", where)))
        sql = "UPDATE `campaigns` SET {0} WHERE {1}".format(sets, cods)
        cursor = db.cursor()
        try:
            cursor.execute(sql, data)
            return cursor.rowcount
        except:
            raise DBError('DB_ERROR')
        finally:
            cursor.close()

    @staticmethod
    def cts_select_one(where):
        # Todo: gop 2 ham one & many thanh 1
        cursor = db.cursor(dictionary=True)
        cods = ' AND '.join(list(map(lambda k: "{0} = %({0})s".format(k), where.keys())))
        try:
            cursor.execute("SELECT * FROM `cdr` WHERE {0} LIMIT 1".format(cods))
            return cursor.fetchone()
        except:
            raise DBError('DB_ERROR')
        finally:
            cursor.close()

    @staticmethod
    def cts_select_many(where):
        cods = ' AND '.join(list(map(lambda k: "{0} = %({0})s".format(k), where.keys())))
        cursor = db.cursor(dictionary=True)
        sql = "SELECT * FROM `cdr` WHERE {0}".format(cods)
        try:
            cursor.execute(sql, filter)
            return cursor.fetchall()
        except:
            raise DBError('DB_ERROR')
        finally:
            cursor.close()

    @staticmethod
    def cts_insert_many(contacts, campaign_id):
        cursor = db.cursor()
        contacts = list(map(lambda c: (campaign_id, int(c['id']), c['phonenumber'], c.get('linkedit', None)), contacts))
        try:
            cursor.executemany("INSERT INTO `cdr`(`campaign_id`, `contact_id`, `phone_number`, `linkedit`)"
                               "VALUES (%s, %s, %s, %s)", contacts)
            return cursor.rowcount
        except:
            raise DBError('DB_ERROR')
        finally:
            cursor.close()

    @staticmethod
    def cts_update(data, where):
        keys = list(filter(lambda u: u not in where, data.keys()))
        sets = ', '.join(list(map(lambda k: "{0} = %({0})s".format(k), keys)))
        cods = ' AND '.join(list(map(lambda w: "{0} = %({0})s", where)))
        sql = "UPDATE `cdr` SET {0} WHERE {1}".format(sets, cods)
        cursor = db.cursor()
        try:
            cursor.execute(sql, data)
            return cursor.rowcount
        except:
            raise DBError('DB_ERROR')
        finally:
            cursor.close()

    def cts_validate(self, contacts):
        valid_contacts = list(filter(lambda c: self.__config['cts_required_field'] in c, contacts))
        if len(valid_contacts) == 0:
            raise CampaignError('CTS_EMPTY')
        return valid_contacts
