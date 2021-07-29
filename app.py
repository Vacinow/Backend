import json
import logging
import re
import os

import boto3
from botocore.exceptions import ClientError
from fastapi import FastAPI, Form, HTTPException, UploadFile, Request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_406_NOT_ACCEPTABLE, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_503_SERVICE_UNAVAILABLE

from models import Endereco, Pessoa, Vacina

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

def db_connect():
    CONNECTION_STRING = "{drivername}://{user}:{passwd}@{host}:{port}/{db_name}".format(
                        drivername=os.environ.get("DB_ENGINE"), 
                        user=os.environ.get("DB_USERNAME"), 
                        passwd=os.environ.get("DB_PASSWORD"), 
                        host=os.environ.get("DB_HOST"), 
                        port=os.environ.get("DB_PORT"), 
                        db_name=os.environ.get("DB_DATABASE"),
                        )
    return create_engine(CONNECTION_STRING, echo=False)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/readfile/")
async def readfile(image: UploadFile = Form(...)):
    try:
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

    except Exception as ex:
        logger.error(ex)
        raise HTTPException(status_code=HTTP_503_SERVICE_UNAVAILABLE, detail="O serviço de OCR não está disponível!")

    try:
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

    except Exception as ex:
        logger.error(ex)
        raise HTTPException(status_code=HTTP_406_NOT_ACCEPTABLE, detail="O formato do formulário não é compatível!")

@app.post("/formsubmit/")
async def formsubmit(request: Request):

    try:
        data = json.loads(await request.body())
        logger.info(json.dumps(data, indent=4, sort_keys=True))
    except Exception as ex:
        logger.error(ex)
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Formato inválido!")

    try:
        engine = db_connect()
        Session = sessionmaker(bind=engine)
        session = Session()
        ## Base.metadata.create_all(engine)
    except Exception as ex:
        logger.error(ex)
        raise HTTPException(status_code=HTTP_503_SERVICE_UNAVAILABLE, detail="Problema ao conectar com base de dados!")

    try:
        for cadastro in data:
            vacinado = Pessoa(
                nome=cadastro.get('name'),
                idade=int(cadastro.get('age')),
                cpf=int(cadastro.get('cpf')),
                cns=int(cadastro.get('nsus')),
            )
            session.add(vacinado)
            vacina = Vacina(
                data_de_aplicacao=cadastro.get('date'),
                tipo=cadastro.get('lab'),
                nome=cadastro.get('vaccine'),
                lote=int(cadastro.get('batch')),
                unidade=cadastro.get('place'),
                pessoa=vacinado
            )
            session.add(vacina)
        
        session.commit()
        session.close()
        return data
    
    except IntegrityError as e:
        logger.error(e)
        session.rollback()
        session.close()
        if isinstance(e.orig, UniqueViolation):
            violation = re.findall('\((.*?)\)', e.orig.diag.message_detail)
            raise HTTPException(status_code=HTTP_406_NOT_ACCEPTABLE, detail=f'O {str(violation[0]).upper()} de número {str(violation[1])} já existe!')
        else:
            raise HTTPException(status_code=HTTP_406_NOT_ACCEPTABLE, detail="Problema ao salvar na base de dados!")

    except Exception as ex:
        logger.error(ex)
        session.rollback()
        session.close()
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Problema ao salvar na base de dados!") 