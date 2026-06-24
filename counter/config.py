import os
from dotenv import load_dotenv
from counter.adapters.count_repo import CountMongoDBRepo, CountInMemoryRepo
from counter.adapters.count_mysql_repo import CountMySQLRepo
from counter.adapters.object_detector import TFSObjectDetector, FakeObjectDetector
from counter.adapters.monitoring import TestMonitor
from counter.adapters.monitoring.mysql_monitor import MysqlMonitor
from counter.domain.actions import CountDetectedObjects, ListDetectedObjects

load_dotenv()

ENV = os.getenv("ENV", "dev")

TFS_HOST = os.getenv("TFS_HOST", "localhost")
TFS_PORT = int(os.getenv("TFS_PORT", 8501))
MODEL_NAME = os.getenv("MODEL_NAME", "ssd_mobilenet_v2")

DB_TYPE = os.getenv("DB_TYPE", "mongodb")

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DB = os.getenv("MYSQL_DB", "counter")

MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
MONGO_DB = os.getenv("MONGO_DB", "prod_counter")


def get_detector():
    return TFSObjectDetector(TFS_HOST, TFS_PORT, MODEL_NAME)

def get_repo():
    if DB_TYPE == "mysql":
        return CountMySQLRepo(host=MYSQL_HOST,port=MYSQL_PORT,user=MYSQL_USER,password=MYSQL_PASSWORD,database=MYSQL_DB)
    return CountMongoDBRepo(host=MONGO_HOST,port=MONGO_PORT,database=MONGO_DB)

def dev_count_action():
    return CountDetectedObjects(FakeObjectDetector(),CountInMemoryRepo())

def dev_object_list_action():
    return ListDetectedObjects(FakeObjectDetector())

def prod_count_action():
    return CountDetectedObjects(get_detector(),get_repo())

def prod_object_list_action():
    return ListDetectedObjects(get_detector())

def get_count_action():
    if ENV == "prod":
        return prod_count_action()
    return dev_count_action()

def get_object_list_action():
    if ENV == "prod":
        return prod_object_list_action()
    return dev_object_list_action()

def get_monitor():
    if ENV != "prod":
        return TestMonitor()
    if DB_TYPE == "mysql":
        return MysqlMonitor(host=MYSQL_HOST,port=MYSQL_PORT,user=MYSQL_USER,password=MYSQL_PASSWORD,database=MYSQL_DB)
    return TestMonitor()