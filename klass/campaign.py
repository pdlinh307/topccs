# -*- coding: utf-8 -*-
from datetime import datetime
from klass.exceptions import CampaignError
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
        if db.select_one(table='cdr', where=dict(campaign_id=cid)):
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
        # Todo: start transaction, rollback if failure
        db.insert_one(table='campaigns', data=dict(campaign_id=cid, time_start=time_start, time_end=time_end))
        cts_valid = list(filter(lambda c: self.__config['required_field_contacts'] in c, data['contact']))
        cts = list(map(lambda c: dict(campaign_id=cid,
                                      contact_id=int(c['id']),
                                      phone_number=c['phonenumber'],
                                      linkedit=c.get('linkedit', None)), cts_valid))
        db.insert_many(table='cdr', data=cts)

        return True
