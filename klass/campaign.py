# -*- coding: utf-8 -*-
import mysql.connector
import configparser
from datetime import datetime
from klass.exceptions import CampaignError


class Campaign(object):
    __instance = None
    __mysql_cnx = None
    __config = None

    @staticmethod
    def get_instance(config):
        """ Static access method """
        if Campaign.__instance is None:
            Campaign(config=config)
        return Campaign.__instance

    def __init__(self, config):
        """ Private constructor """
        if Campaign.__instance is not None:
            raise CampaignError('CP_SINGLETON_CLASS')
        else:
            Campaign.__instance = self
            self.__config = configparser.ConfigParser()
            self.__config.read(config)

    def __del__(self):
        self.__mysql_cnx.close()

    def db_connect(self, dbconfig):
        try:
            self.__mysql_cnx = mysql.connector.connect(option_files=dbconfig)
        except:
            raise CampaignError('DB_CONNECT_ERROR')

    def cp_check_payload(self, json):
        required_fields = self.__config['send_campaign']['cp_required_fields'].split(',')
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

    def cp_select_one(self, campaign_id):
        cursor = self.__mysql_cnx.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM `campaigns` WHERE `campaign_id` = %s LIMIT 1", (campaign_id,))
            return cursor.fetchone()
        except:
            raise CampaignError('DB_ERROR')
        finally:
            cursor.close()

    def cp_insert_one(self, json):
        try:
            date_format = self.__config['send_campaign']['cp_datetime_format']
            time_start = datetime.strptime(json['starttime'], date_format)
            time_end = datetime.strptime(json['endtime'], date_format)
            if time_end < time_start or time_end < datetime.now():
                raise CampaignError('CP_INVALID_PARAM')
        except ValueError:
            raise CampaignError('CP_DATETIME_FORMAT')

        cursor = self.__mysql_cnx.cursor(dictionary=True)
        try:
            cursor.execute("INSERT INTO `campaigns`(`campaign_id`, `type_id`, `time_start`, `time_end`)"
                           "VALUES (%s, %s, %s, %s)",
                           (int(json['campaignid']), int(json['typeid']), time_start, time_end))
            return cursor.rowcount
        except:
            raise CampaignError('DB_ERROR')
        finally:
            cursor.close()

    def cp_close_one(self, campaign_id):
        row = self.cp_select_one(campaign_id)
        if row is None:
            raise CampaignError('CP_ID_NOT_EXISTED')
        cursor = self.__mysql_cnx.cursor(dictionary=True)
        try:
            cursor.execute("UPDATE `campaigns` SET `status_closed` = TRUE WHERE `campaign_id` = %s", (campaign_id,))
            return cursor.rowcount
        except:
            raise CampaignError('DB_ERROR')
        finally:
            cursor.close()

    def cts_get_valid_list(self, contacts):
        valid_contacts = list(filter(lambda c: self.__config['send_campaign']['cts_required_field'] in c, contacts))
        if len(valid_contacts) == 0:
            raise CampaignError('CTS_EMPTY')
        return valid_contacts

    def cts_insert_many(self, contacts, campaign_id):
        cursor = self.__mysql_cnx.cursor(dictionary=True)
        contacts = list(map(lambda c: (campaign_id, int(c['id']), c['phonenumber'], c.get('linkedit', None)), contacts))
        try:
            cursor.executemany("INSERT INTO `cdr`(`campaign_id`, `contact_id`, `phone_number`, `linkedit`)"
                               "VALUES (%s, %s, %s, %s)", contacts)
            return cursor.rowcount
        except:
            raise CampaignError('DB_ERROR')
        finally:
            cursor.close()

    # Todo: create schedule