from fastapi import FastAPI, HTTPException, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import uuid

import boto3
from botocore.exceptions import ClientError

import logging

BUCKET_NAME = 'vacinow'

logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/readfile/")
async def readfile(image: UploadFile = Form(...)):
    # Upload the file
    file_id = str(uuid.uuid4())
    s3 = boto3.client('s3')
    try:
        s3.upload_fileobj(image.file, BUCKET_NAME, file_id)        
    except ClientError as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Can't process image")
    return {"filename": str(image.filename)}

handler = Mangum(app=app)