import pickle
import os
from pathlib import Path

from cos_access.helper import BucketHelper
from niulib.api import NiuApi

BASEPATH = Path("/tmp/niulib_running_files")
DBPATH = BASEPATH.joinpath("data")
NAPIPKLPATH = DBPATH.joinpath("napi.pkl")

BASEPATH = BASEPATH.relative_to("/").as_posix()
DBPATH = DBPATH.relative_to("/").as_posix()
NAPIPKLPATH = NAPIPKLPATH.relative_to("/").as_posix()


def loadApi() -> NiuApi:
    helper = BucketHelper()
    try:
        with helper.get_object(NAPIPKLPATH) as f:
            obj = pickle.load(f)
    except Exception as e:
        print(e)
        obj = getNewApi()
    assert isinstance(obj, NiuApi)
    return obj


def getNewApi() -> NiuApi:
    account_name = os.environ.get("NIU_ACCOUNT_NAME")
    account_md5 = os.environ.get("NIU_ACCOUNT_MD5")
    assert account_name
    assert account_md5
    napi = NiuApi(account_name, "", 0, md5=account_md5)
    napi.initApi()
    helper = BucketHelper()
    with helper.sponge_file(NAPIPKLPATH) as f:
        pickle.dump(napi, f)
    return napi


def fetchApi() -> NiuApi:
    if BucketHelper().object_exists(NAPIPKLPATH):
        obj = loadApi()
        if obj.expired():
            obj = getNewApi()
    else:
        obj = getNewApi()
    return obj
