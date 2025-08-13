import pyodbc
from pymongo import MongoClient
from Utils.V1.config_reader import configure


ms_connection_string = (
    'DRIVER='+configure.get('DB', 'DRIVER')+';'
    'SERVER=' + configure.get('DB', 'HOST') + ';'
    'DATABASE=' + configure.get('DB', 'DATABASE') + ';'
    'UID=' + configure.get('DB', 'USERNAME') + ';'
    'PWD=' + configure.get('DB', 'PASSWORD') + ';'
    'MARS_Connection=Yes;'

)
msdb = pyodbc.connect(ms_connection_string)
msdb.autocommit = True
# cursor = msdb.cursor()


def get_db_cursor():
    with msdb.cursor() as cursor:
        yield cursor


# MongoDB connection URI
uri = "mongodb://" + configure.get('DB', 'USERNAME') + ":" + configure.get('DB', 'PASSWORD') + "@" + configure.get('DB', 'HOST') + ":" + configure.get('DB', 'MPORT') + "/?authSource=" + configure.get('DB', 'SOURCE')
# uri = "mongodb://sa:963852@192.168.102.120:27017/?authSource=admin"
client = MongoClient(uri)
db = client["DRIVE_SHARING"]

# Create collections
drive_collection = db["drive"]
sharing_collection = db["sharing"]
group_collection = db["group"]
favorites_collection = db['favorites']



