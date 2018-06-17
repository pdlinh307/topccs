import mysql.connector
import datetime
from exceptions import CampaignError


class Campaign(object):
    __required_fields = ['campaignid', 'typeid', 'contact', 'code']
    # __mysql_cnx = None

    def __init__(self):
        self.__mysql_cnx = mysql.connector.connect(option_files='config/mysql.conf')

    def check_payload(self, json):
        if json is None:
            raise CampaignError('CP_NO_PAYLOAD')
        for f in self.__required_fields:
            if f not in json:
                raise CampaignError('CP_MISS_PARAM')
        return True

    def check_unique_id(self, campaign_id):
        row = self.select_one(campaign_id)
        if row.__len__ == 1:
            raise CampaignError('CP_ID_EXIST')
        return True

    def select_one(self, campaign_id):
        cursor = self.__mysql_cnx.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM `campaign` WHERE `id` = %s LIMIT 1", (campaign_id,))
            return cursor.fetchone()
        except:
            raise CampaignError('CP_DB_ERROR')

    def insert_one(self, json):
        # todo: parsing date time from input data
        cursor = self.__mysql_cnx.cursor(dictionary=True)
        try:
            cursor.execute("INSERT INTO `campaign`"
                           "(`id`, `name`, `start`, `end`, `type_id`, `code`, `receive_status`) "
                           "VALUES (%s, %s, %s, %s, %s, %s)",
                           (json['campaignid'], '', datetime.datetime(2018, 6, 6, 14, 0, 0)),
                           datetime.datetime(2018, 6, 10, 20, 0, 12), json['type_id'], json['code'])
            return cursor.lastrowid
        except:
            raise CampaignError('CP_DB_ERROR')
