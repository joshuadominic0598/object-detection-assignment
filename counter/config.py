import os

from counter.adapters.count_repo import CountMongoDBRepo, CountInMemoryRepo
from counter.adapters.object_detector import TFSObjectDetector, FakeObjectDetector
from counter.domain.actions import CountDetectedObjects,ListDetectedObjects


def dev_count_action() -> CountDetectedObjects:
    return CountDetectedObjects(FakeObjectDetector(), CountInMemoryRepo())

def dev_object_list_action() -> ListDetectedObjects:
    return ListDetectedObjects(FakeObjectDetector())

def prod_count_action() -> CountDetectedObjects:
    tfs_host = os.environ.get('TFS_HOST', 'localhost')
    tfs_port = os.environ.get('TFS_PORT', 8501)
    mongo_host = os.environ.get('MONGO_HOST', 'localhost')
    mongo_port = os.environ.get('MONGO_PORT', 27017)
    mongo_db = os.environ.get('MONGO_DB', 'prod_counter')
    model_name = os.environ.get('MODEL_NAME', 'ssd_mobilenet_v2')
    return CountDetectedObjects(TFSObjectDetector(tfs_host, tfs_port, model_name),
                                CountMongoDBRepo(host=mongo_host, port=mongo_port, database=mongo_db))

def prod_object_list_action():
    tfs_host = os.environ.get('TFS_HOST', 'localhost')
    tfs_port = os.environ.get('TFS_PORT', 8501)
    model_name = os.environ.get('MODEL_NAME', 'ssd_mobilenet_v2')
    return ListDetectedObjects(TFSObjectDetector(tfs_host,tfs_port,model_name))

def get_count_action() -> CountDetectedObjects:
    env = os.environ.get('ENV', 'dev')
    count_action_fn = f"{env}_count_action"
    return globals()[count_action_fn]()

def get_object_list_action():
    env = os.environ.get('ENV', 'dev')
    action_fn = f"{env}_object_list_action"
    return globals()[action_fn]()