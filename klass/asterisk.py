# -*- coding: utf-8 -*-
from datetime import datetime
from asterisk.ami import AMIClient, AutoReconnect, EventListener
from klass.singleton import Singleton
from klass.campaign import Campaign


class AsteriskAMI(metaclass=Singleton):
    __client = None
    __config = None

    def __init__(self, config):
        self.__config = config
        self.__client = AMIClient(address=self.__config['host'], port=int(self.__config['port']))
        future = self.__client.login(username=self.__config['username'], secret=self.__config['secret'])
        if future.response.is_error():
            raise Exception(str(future.response))
        AutoReconnect(self.__client)
        self.__client.add_event_listener(EventListener(on_event=self.__event_listener_cdr, white_list='Cdr'))

    def __del__(self):
        self.__client.logoff()

    def __event_listener_cdr(self, source, event):
        response = event.keys
        if Campaign.cts_select_many(where=dict(uniqueid=response['UniqueID'])):
            fmt = self.__config['datetime_format']
            cdr = dict(
                time_start=datetime.strftime(response['StartTime'], fmt),
                time_end=datetime.strftime(response['EndTime'], fmt),
                agent=response['Source'],
                station_id=response['Source'],
                duration=response['Duration'],
                billsec=response['BillableSeconds'],
                disposistion=response['Disposition'],
                uniqueid=response['UniqueID'],
                linkedid=response['Linkedid']
            )
            cdr['record_url'] = response['RecordingFile']
            if response['AnswerTime'] != '':
                cdr['time_answer'] = datetime.strftime(response['AnswerTime'], fmt)
            Campaign.cts_update(data=cdr, where=['uniqueid'])
