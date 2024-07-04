import hashlib
import logging
import os
from datetime import datetime as dt_datetime, time as dt_time, timedelta as dt_timedelta
from typing import Dict

from cos_access.helper import BucketHelper

from fastapi import FastAPI
from pydantic import BaseModel
from niulib.lib import fetchApi, NiuApi

app = FastAPI()
logger = logging.getLogger("niulib_webserver")
LAST_CONNECTED_PATH = "/tmp/niulib_running_files/last_connected"

logging.basicConfig(level=logging.INFO)


class BaseVerify(BaseModel):
    time: str
    md5: str


class NiuConRequest(BaseVerify):
    niu_con: str


def failed(reason: str):
    return {"status": "failed", "reason": reason}


def ok(**kwargs):
    assert "status" not in kwargs
    rtn = {"status": "ok"}
    rtn.update(kwargs)
    return rtn


def verify(payload: BaseVerify):
    time = payload.time
    md5 = payload.md5
    request_datetime = dt_datetime.fromisoformat(time).timestamp()
    now_time = dt_datetime.now().timestamp()
    delta = now_time - request_datetime
    if abs(delta) > 30:
        return failed("time is not correct")
    salt = os.environ.get("NIU_SALT", "default_salt")
    gt_md5 = hashlib.md5(f"{salt}{time}api".encode()).hexdigest()
    if gt_md5 != md5:
        return failed("md5 is not correct")
    return None


@app.post("/niu_conn")
async def niu_conn(payload: BaseVerify):
    rtn = verify(payload)
    if rtn is not None:
        return rtn
    last_connected = dt_datetime.now().timestamp()
    with BucketHelper().sponge_file(LAST_CONNECTED_PATH) as f:
        f.write(str(last_connected).encode())
    return ok(last_connected=last_connected)


@app.post("/acc_off")
async def acc_off(payload: BaseVerify):
    rtn = verify(payload)
    if rtn is not None:
        return rtn
    api = fetchApi()
    resp = api.action("acc_off")
    return ok(is_acc_on=api.updateMoto().is_acc_on())


@app.post("/acc_on")
async def acc_on(payload: BaseVerify):
    rtn = verify(payload)
    if rtn is not None:
        return rtn
    api = fetchApi()
    resp = api.action("acc_on")
    return ok(is_acc_on=api.updateMoto().is_acc_on())


@app.post("/toggle_acc")
async def toggle_acc(payload: NiuConRequest):
    rtn = verify(payload)
    if rtn is not None:
        return rtn
    api = fetchApi().updateMoto()
    now_ts = dt_datetime.now().timestamp()
    try:
        with BucketHelper().get_object(LAST_CONNECTED_PATH) as f:
            last_connected = float(f.read().decode())
    except Exception as e:
        last_connected = 0
    if payload.niu_con == "1" or now_ts - last_connected < 60:
        # Toggle Acc
        if api.is_acc_on():
            resp = api.action("acc_off")
        else:
            resp = api.action("acc_on")
        return ok(is_acc_on=api.updateMoto().is_acc_on(), resp=resp)
    else:
        if api.updateMoto().is_acc_on():
            resp = api.action("acc_off")
            return ok(is_acc_on=api.updateMoto().is_acc_on(), resp=resp)
        logger.info("Refuse to switch on because NIU not connected")
    return failed("NIU not connected")
