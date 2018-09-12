# -*- coding: utf-8 -*-
#!/usr/bin/python3.6

import asyncio
from datetime import datetime
from panoramisk.manager import Manager
from klass import conf, db
import cworker

ami = Manager(loop=asyncio.get_event_loop(), **conf.section(name='asterisk'))


@ami.register_event('Cdr')
def listener_cdr(manager, event):
    if not db.select_one(table='cdr', where=dict(uniqueid=event['UniqueID'])):
        return False
    fmt = "%Y-%m-%d %H:%M:%S"
    cdr = dict(
        time_start=datetime.strptime(event['StartTime'], fmt),
        time_end=datetime.strptime(event['EndTime'], fmt),
        agent=event['Destination'],
        station_id=event['Destination'],
        duration=event['Duration'],
        billsec=event['BillableSeconds'],
        disposition=event['Disposition'],
        uniqueid=event['UniqueID'],
        linkedid=event['Linkedid']
    )
    if event['RecordingFile'] != '':
        cdr['record_url'] = conf.section(name='originate')['record_url'] + event['RecordingFile']
    if event['AnswerTime'] != '':
        cdr['time_answer'] = datetime.strptime(event['AnswerTime'], fmt)
    db.update(table='cdr', where=['uniqueid'], data=cdr)
    cworker.callback_cdr.delay(callid=event['UniqueID'])


if __name__ == '__main__':
    try:
        ami.connect()
        ami.loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        ami.loop.close()
