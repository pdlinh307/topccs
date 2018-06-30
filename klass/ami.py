# -*- coding: utf-8 -*-
import asyncio
from panoramisk import CallManager, Manager
from klass.singleton import Singleton


class AsteriskAMI(metaclass=Singleton):
    __ami = None
    __config = None

    def __init__(self, config):
        self.__config = config
        self.__ami = self.connect()

    def connect(self):
        return Manager(loop=asyncio.get_event_loop(),
                       host=self.__config['host'],
                       username=self.__config['username'],
                       secret=self.__config['secret'])


import asyncio
import getopt
import json
import sys
from configparser import ConfigParser, Error

import mysql.connector as mariadb
from panoramisk import Manager
from redis import Redis, ConnectionError

# Load config
conf_filename = '/etc/crawler.conf'
try:
    conf = ConfigParser()
    conf.read(conf_filename)
except Error as e:
    print(e.msg)
    sys.exit(1)

system = conf.get('general', 'system')

# Asterisk manager interface
ami = Manager(loop=asyncio.get_event_loop(),
              host=conf.get('asterisk', 'host'),
              username=conf.get('asterisk', 'ami_username'),
              secret=conf.get('asterisk', 'ami_secret'))

# Redis message queue
redis_cli = Redis(host=conf.get('redis', 'host'),
                  port=int(conf.get('redis', 'port')),
                  db=int(conf.get('redis', 'db')))


# AMI register event
@ami.register_event('*')
def callback(event, manager):
    message = dict()
    for item in manager.items():
        message[item[0]] = item[1]
        message['log_type'] = 'ami'

    if 'SystemName' not in message:
        message['SystemName'] = system

    try:
        redis_cli.rpush('ami', json.dumps(message))
    except ConnectionError as e:
        print(e.message)


def main(argv):
    if len(argv) > 0:
        try:
            opts, args = getopt.getopt(argv, "h:s:", ["sync="])
        except getopt.GetoptError:
            print("Usage: crawlerd -s <object_name>")
            sys.exit(2)
        for opt, arg in opts:
            if opt == '-h':
                print("Usage: crawlerd -s <object_name>")
                sys.exit(2)
            elif opt in ('-s', '--sync'):
                if arg == 'extensions':
                    try:
                        # MariaDB connect
                        mariadb_conn = mariadb.connect(host=conf.get('mariadb', 'host'),
                                                       port=int(conf.get('mariadb', 'port')),
                                                       database=conf.get('mariadb', 'database'),
                                                       user=conf.get('mariadb', 'user'),
                                                       password=conf.get('mariadb', 'password'))
                    except mariadb.Error as err:
                        print(err)
                        sys.exit(1)
                    mariadb_cursor = mariadb_conn.cursor()
                    query = ("SELECT sip.`id`, sip.`data` AS `secret`, users.`name` "
                             "FROM `sip` LEFT JOIN `users` ON sip.`id` = users.`extension` "
                             "WHERE sip.`keyword` = 'secret'")
                    mariadb_cursor.execute(query)
                    for (ext, secret, name) in mariadb_cursor:
                        redis_cli.rpush('exts', json.dumps(dict(extension=ext,
                                                                secret=secret,
                                                                name=name,
                                                                log_type='exts',
                                                                system=system)))
                    mariadb_cursor.close()
                    mariadb_conn.close()
                    print("Done!\n")
                elif arg == 'queues':
                    try:
                        # MariaDB connect
                        mariadb_conn = mariadb.connect(host=conf.get('mariadb', 'host'),
                                                       port=int(conf.get('mariadb', 'port')),
                                                       database=conf.get('mariadb', 'database'),
                                                       user=conf.get('mariadb', 'user'),
                                                       password=conf.get('mariadb', 'password'))
                    except mariadb.Error as err:
                        print(err)
                        sys.exit(1)
                    mariadb_cursor = mariadb_conn.cursor()
                    query = ("SELECT queues_details.`id`, queues_config.`descr`, GROUP_CONCAT(queues_details.`data` SEPARATOR ';') AS member "
                             "FROM `queues_details` LEFT JOIN `queues_config` ON queues_details.`id` = queues_config.`extension` "
                             "WHERE queues_details.`keyword` = 'member' "
                             "GROUP BY queues_details.`id` ")
                    mariadb_cursor.execute(query)
                    for (queue, name, member) in mariadb_cursor:
                        redis_cli.rpush('queues', json.dumps(dict(queue=queue,
                                                                  name=name,
                                                                  member=member,
                                                                  log_type='queues',
                                                                  system=system)))
                    mariadb_cursor.close()
                    mariadb_conn.close()
                    print("Done!\n")
                else:
                    print("Object %s is not available" % arg)
                    sys.exit(2)

    else:
        ami.connect()
        try:
            ami.loop.run_forever()
        except KeyboardInterrupt:
            ami.loop.close()
            sys.exit(0)


if __name__ == '__main__':
    main(sys.argv[1:])