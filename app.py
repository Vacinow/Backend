from fastapi import FastAPI, HTTPException, UploadFile, Form, status

import boto3
from botocore.exceptions import ClientError

import logging
import json
import re

from starlette.requests import Request

from models import Pessoa, Vacina, Endereco

logger = logging.getLogger()
logger.setLevel(logging.INFO)

KEY_WORDS = [
    "Nome",
    "Idade",
    "CPF",
    "Data aplicação",
    "Nome da vacina",
    "Serviço de Saúde",
    "Local de aplicação",
    "Laboratório",
    "Lote"
]

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/readfile/")
async def readfile(image: UploadFile = Form(...)):

    size = 4

    textract = boto3.client('textract')
    logger.info('connected to textract')
    response = textract.detect_document_text(
    Document={
        'Bytes': image.file.read()
    })
    text = ''
    for item in response["Blocks"]:
        if item["BlockType"] == "WORD":
            text += (' ' + item["Text"])
    
    data = []

    for i in range(size):
        tmp = {}
        for j in range(len(KEY_WORDS) - 1):
            result = re.search(KEY_WORDS[j] + '(.*?)' + KEY_WORDS[j+1], text)
            text = text[len(result.group(1)):]
            tmp[KEY_WORDS[j]] = result.group(1)
        data.append(tmp)
    
    return data

@app.post("/formsubmit/")
async def formsubmit(request: Request):
    data = json.loads(await request.body())
    return data