# -*- coding: utf-8 -*-
import configparser
from klass.singleton import Singleton


class AppConfig(metaclass=Singleton):
    __config = None

    def __init__(self, file):
        self.__config = configparser.ConfigParser()
        self.__config.read(file)

    def section(self, name):
        return self.__config[name]
