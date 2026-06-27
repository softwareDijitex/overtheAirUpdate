import json
import uuid
import time

from io import BytesIO

from fastapi import FastAPI, UploadFile, File, Request

from fastapi.responses import StreamingResponse
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import Message
from pydantic import BaseModel

import paho.mqtt.client as mqtt


app = FastAPI()

mqtt_client = mqtt.Client()

mqtt_client.connect("localhost",1883)

mqtt_client.loop_start()

waiting_reports = {}


class ReportRequest(BaseModel):

    mac_address:str


@app.post("/api/test/report")

async def test_report(request:ReportRequest):

    mac = request.mac_address.replace(":","").upper()

    registry_manager = IoTHubRegistryManager(connection_string="HostName=ReportGeneration.azure-devices.net;SharedAccessKeyName=service;SharedAccessKey=It64BU5c/+aikRFBi+BVdgDfXeJBIMekVAIoTBPp3YU=")
    request_id=str(uuid.uuid4())
    payload = {
    "requestId": "12345",
    "command": "generate_report"
    }
    message = Message(json.dumps(payload))

    registry_manager.send_c2d_message(
    "9c9e6e14c138",    # Device ID in IoT Hub
    message
    )
    timeout=60

    start=time.time()

    while True:

        if request_id in waiting_reports:

            report = waiting_reports.pop(request_id)

            return StreamingResponse(
                    BytesIO(report["data"]),
                    media_type=report["content_type"],
                    headers={ "Content-Disposition":
                    f'attachment; filename="{report["filename"]}"'}
                )

        if time.time()-start>timeout:

            return {"error":"Timeout"}

        time.sleep(.5)


@app.post("/api/hardware/report/upload")
async def upload_report(
    request: Request,
    file: UploadFile = File(...)
):

    file_bytes = await file.read()

    filename = file.filename
    content_type = file.content_type

    request_id = request.headers["Request-Id"]

    waiting_reports[request_id] = {
        "filename": filename,
        "content_type": content_type,
        "data": file_bytes
    }

    return {"success": True}