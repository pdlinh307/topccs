import configparser
from klass.exceptions import ConfigError


class AppConfig(object):
    __instance = None
    __config = None
    __file_path = None

    @staticmethod
    def get_instance(filepath):
        """ Static access method """
        if AppConfig.__instance is None:
            AppConfig(filepath=filepath)
        return AppConfig.__instance

    def __init__(self, filepath):
        """ Private constructor """
        if AppConfig.__instance is not None:
            raise ConfigError('CF_SINGLETON_CLASS')
        AppConfig.__instance = self
        self.__config = configparser.ConfigParser()
        self.__config.read(filepath)

    def get_section(self, name):
        return self.__config[name]
