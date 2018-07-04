#!/usr/bin/python3.6
# import sys
import asyncio
from panoramisk.call_manager import CallManager
from klass import conf


@asyncio.coroutine
def originate():
    phone = '0967289229'
    conf_trunk = conf.section(name='trunk')
    callmanager = CallManager()
    yield from callmanager.connect()
    call = yield from callmanager.send_originate({
        'Action': 'Originate',
        'Channel': '{0}/{1}'.format(conf_trunk['channel'], phone),
        'Timeout': 20000,
        'CallerID': phone,
        'Exten': '1001',
        'Context': conf_trunk['context'],
        'Priority': 1
    })
    callmanager.clean_originate(call)
    callmanager.close()


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(originate())
    loop.close()


if __name__ == '__main__':
    main()