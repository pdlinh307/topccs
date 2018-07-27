# -*- coding: utf-8 -*-
#!/usr/bin/python3.6

import sys
import getopt
import asyncio
from panoramisk.manager import Manager
from klass import conf, db


@asyncio.coroutine
def queue_status(queue):
    conf_asterisk = conf.section(name='asterisk')
    manager = Manager(**conf_asterisk)

    yield from manager.connect()
    queues_status = yield from manager.send_action(
        {'Action': 'QueueStatus', 'Queue': queue})
    manager.close()

    available_extensions = list(filter(lambda x: 'Status' in x and x['Status'] == '1', queues_status))
    if len(available_extensions) == 0:
        print('')
    else:
        available_extensions_sorted = sorted(available_extensions, key=lambda k: k['CallsTaken'])
        print(available_extensions_sorted[0]['Name'])


@asyncio.coroutine
def originate(cdrid, extension):
    conf_originate = conf.section(name='originate')
    conf_asterisk = conf.section(name='asterisk')

    job = db.select_one(table='cdr', where=dict(id=cdrid))

    manager = Manager(**conf_asterisk)
    yield from manager.connect()
    action = dict(
        Action='Originate',
        Channel='{0}/{1}'.format(conf_originate['channel'], job['phone_number']),
        Context=conf_originate['context'],
        Exten=extension,
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
    if len(argv) > 0:
        try:
            opts, args = getopt.getopt(argv, "o:q:", ["queue="])
        except getopt.GetoptError:
            print("Usage: originate -q <queue_name>")
            sys.exit(2)

        for opt, arg in opts:
            if opt in ('-q', '--queue'):
                loop = asyncio.get_event_loop()
                loop.run_until_complete(queue_status(queue=arg))
                loop.close()
            elif opt == '-o':
                loop = asyncio.get_event_loop()
                loop.run_until_complete(originate(cdrid=int(arg), extension=args[0]))
                loop.close()


if __name__ == '__main__':
    main(sys.argv[1:])
