from fastapi import FastAPI, HTTPException, UploadFile, Form
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import uuid

import boto3
from botocore.exceptions import ClientError

import logging

BUCKET_NAME = 'vacinowbucket'

logger = logging.getLogger()
logger.setLevel(logging.INFO)


middleware = [Middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])]
app = FastAPI(middleware=middleware)

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.post("/readfile/")
def readfile(image: UploadFile = Form(...)):
    # Upload the file
    file_format = image.filename.split('.')[-1]
    file_id = str(uuid.uuid4())+'.'+file_format
    s3 = boto3.client('s3', region_name = 'us-east-1')
    logger.info('connected to s3')
    try:
        s3.upload_fileobj(image.file, BUCKET_NAME, file_id) 
        logger.info('uploaded')       
    except ClientError as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Can't process image")
    
    # Reading text
    textract = boto3.client('textract', region_name = 'us-east-1')
    logger.info('connected to textract')
    logger.info(file_id)
    response = textract.detect_document_text(
    Document={
        'S3Object': {
            'Bucket': BUCKET_NAME,
            'Name': file_id
        }
    })
    text = ''
    for item in response["Blocks"]:
        if item["BlockType"] == "LINE":
            text += (item["Text"] + '\n')
    logger.info(text)
    return {"text": text}

handler = Mangum(app=app)