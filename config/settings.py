from json import load
from os import listdir
from os.path import join, dirname, abspath
from logging import _nameToLevel as nameToLevel

__author__ = 'fla'

__version__ = '0.5.0'

# Settings file is inside Basics directory, therefore I have to go back to the parent directory
# to have the Code Home directory
CODEHOME = dirname(dirname(abspath(__file__)))
LOGHOME = join(CODEHOME, 'logs')
CONFIGFILE = join(join(CODEHOME, "config"), 'configuration.json')

# Reading some configuration
with open(CONFIGFILE, 'r') as f:
    configuration = load(f)

# NGSI-LD Context
AT_CONTEXT = configuration['context']
configuration.pop('context')

# CSV_FOLDER should start without any '/', the folder in which the csv files are included, relative to the code
DATA_FOLDER = configuration['files']
configuration.pop('files')

# URL for entities
URL_BROKER = configuration['broker']
configuration.pop('broker')

# LOG LEVEL
LOGLEVEL = configuration['log_level']

try:
    LOGLEVEL = nameToLevel[LOGLEVEL]
except Exception as e:
    print('Invalid log level: {}'.format(LOGLEVEL))
    print('Please use one of the following values:')
    print('   * CRITICAL')
    print('   * ERROR')
    print('   * WARNING')
    print('   * INFO')
    print('   * DEBUG')
    print('   * NOTSET')
    exit()

configuration.pop('log_level')

# Scope
try:
    SCOPE = configuration['scope']
    configuration.pop('scope')
except KeyError as e:
    # It is not defined scope, therefore the default value is 0
    SCOPE = 0

# Absolute path to the csv files, it is fixed to the relative path of this script
DATAHOME = join(CODEHOME, DATA_FOLDER)

# List of all csv files to process
TEMP = configuration["temperature"]
TEMP = list(map(lambda x: (x, join(DATAHOME, x)), TEMP))

RAIN_GAUGE = configuration["rain_gauge"]
RAIN_GAUGE = (RAIN_GAUGE, join(DATAHOME, RAIN_GAUGE))

LEVEL_METER = configuration["level_meter"]
LEVEL_METER = (LEVEL_METER, join(DATAHOME, LEVEL_METER))

FILES = TEMP + [RAIN_GAUGE] + [LEVEL_METER]

configuration.pop('temperature')
configuration.pop('rain_gauge')
configuration.pop('level_meter')
