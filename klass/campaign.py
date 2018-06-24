# -*- coding: utf-8 -*-
import mysql.connector
from datetime import datetime, timedelta
from klass.exceptions import CampaignError


class Campaign(object):
    __instance = None
    __mysql_cnx = None

    @staticmethod
    def get_instance():
        """ Static access method """
        if Campaign.__instance is None:
            Campaign()
        return Campaign.__instance

    def __init__(self):
        """ Private constructor """
        if Campaign.__instance is not None:
            raise CampaignError('CP_SINGLETON_CLASS')
        else:
            Campaign.__instance = self

    def db_connect(self, config):
        try:
            self.__mysql_cnx = mysql.connector.connect(option_files=config)
        except:
            raise CampaignError('DB_CONNECT_ERROR')

    def check_payload(self, json):
        required_fields = ['campaignid', 'typeid', 'contact', 'code', 'start_time', 'end_time']
        if json is None:
            raise CampaignError('CP_NO_PAYLOAD')
        for f in required_fields:
            if f not in json:
                raise CampaignError('CP_MISS_PARAM')
        return True

    def check_unique_id(self, campaign_id):
        row = self.select_one(campaign_id)
        if row.__len__() == 1:
            raise CampaignError('CP_ID_EXIST')
        return True

    def select_one(self, campaign_id):
        cursor = self.__mysql_cnx.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM `campaigns` WHERE `campaign_id` = %s LIMIT 1", (campaign_id,))
            return cursor.fetchone()
        except:
            raise CampaignError('CP_DB_ERROR')

    def insert_one(self, json):
        time_start = datetime.strptime(json['start_time'], 'YYYY-MM-DDTHH:MM:SS.mmmmmm')
        time_end = datetime.strptime(json['end_time'], 'YYYY-MM-DDTHH:MM:SS.mmmmmm')
        if time_end < time_start or time_end < datetime.now():
            raise CampaignError('CP_DATA_INVALID')
        cursor = self.__mysql_cnx.cursor(dictionary=True)
        try:
            cursor.execute("INSERT INTO `campaigns`"
                           "(`campaign_id`, `type_id`, `code`, `time_start`, `time_end`, `status_received`, `number_contacts`)"
                           "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                           (json['campaignid'], json['typeid'], json['code'], time_start, time_end, True, len(json['contact'])))
        except:
            raise CampaignError('CP_DB_ERROR')
        else:
            return cursor.lastrowid

    # Todo: create schedule