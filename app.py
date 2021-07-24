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
    ("Nome", "name"),
    ("Idade", "age"),
    ("CPF", "cpf"),
    ("Data aplicação", "date"),
    ("Nome da vacina", "vaccine"),
    ("Serviço de Saúde", "nsus"),
    ("Local de aplicação", "place"),
    ("Laboratório", "lab"),
    ("Lote", "batch")
]

DEFAULT_SIZE = 11

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
        if item["BlockType"] == "WORD":
            text += (' ' + item["Text"])

    data = []

    for i in range(DEFAULT_SIZE):
        tmp = {}
        for j in range(len(KEY_WORDS)):
            n = j+1 if j+1 < len(KEY_WORDS) else 0
            if i == DEFAULT_SIZE-1 and n == 0:
                result = re.search(KEY_WORDS[j][0] + '(.*)', text)
            else:
                result = re.search(KEY_WORDS[j][0] + '(.*?)' + KEY_WORDS[n][0], text)
            text = text[len(KEY_WORDS[j][0] + result.group(1)):]
            tmp[KEY_WORDS[j][1]] = result.group(1).lstrip().rstrip()
        data.append(tmp)

    return data

@app.post("/formsubmit/")
async def formsubmit(request: Request):
    data = json.loads(await request.body())
    return data