from fastapi import FastAPI, HTTPException, UploadFile, Form

import boto3
from botocore.exceptions import ClientError

import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/readfile/")
async def readfile(image: UploadFile = Form(...)):

    textract = boto3.client('textract')
    logger.info('connected to textract')
    response = textract.detect_document_text(
    Document={
        'Bytes': image.file.read()
    })
    text = ''
    for item in response["Blocks"]:
        if item["BlockType"] == "LINE":
            text += (item["Text"] + '\n')
    logger.info(text)
    return {"text": text}