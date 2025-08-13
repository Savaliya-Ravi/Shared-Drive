from configparser import ConfigParser
import os
from Constant.general import PROJECT

loc = os.getcwd().split(PROJECT)
path = os.path.join(loc[0], f'{PROJECT}/config.ini')

configure = ConfigParser()
configure.read(path)
