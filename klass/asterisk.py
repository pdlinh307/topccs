# -*- coding: utf-8 -*-
import asyncio
import sys
import pprint
from panoramisk import CallManager, Manager
from klass.singleton import Singleton
from klass.campaign import Campaign


class AsteriskAMI(metaclass=Singleton):
    __manager = None
    __config = None

    def __init__(self, config):
        self.__config = config
        self.__manager = Manager(**self.__config)

    def __del__(self):
        self.__manager.loop.close()

    def run_forever(self):
        self.__manager.connect()
        self.__manager.loop.run_forever()

    def register_event(self, pattern, callback):
        self.__manager.register_event(pattern, callback)

    def action(self, command):
        yield from self.__manager.connect()
        action_results = yield from self.__manager.send_action(**command)
        self.__manager.close()

