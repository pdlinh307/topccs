# -*- coding: utf-8 -*-
#!/usr/bin/python3.6

import sys
import asyncio
from panoramisk.manager import Manager
from klass import conf, db


@asyncio.coroutine
def originate(rid):
    conf_originate = conf.section(name='originate')
    conf_asterisk = conf.section(name='asterisk')

    job = db.select_one(table='cdr', where=dict(id=rid))

    manager = Manager(**conf_asterisk)
    yield from manager.connect()
    action = dict(
        Action='Originate',
        Channel='{0}/{1}'.format(conf_originate['channel'], job['phone_number']),
        Context=conf_originate['context'],
        Exten='1001',
        Priority=conf_originate['priority'],
        Timeout=int(conf_originate['timeout']),
        WaitTime=25,
        CallerID=job['phone_number'],
        Async=True
    )
    responses = yield from manager.send_action(action=action, as_list=True)
    manager.close()

    print(responses[1]['Uniqueid'])


def main(argv):
    if len(argv) > 1:
        rid = int(argv[1])
        loop = asyncio.get_event_loop()
        loop.run_until_complete(originate(rid=rid))
        loop.close()


if __name__ == '__main__':
    main(sys.argv)