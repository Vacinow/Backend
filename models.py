from sqlalchemy import create_engine, Column, Table, ForeignKey, MetaData
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (Integer, String, Date, DateTime, Float, Boolean, Text)
from sqlalchemy.sql.schema import CheckConstraint
import os
import logging

Base = declarative_base()

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

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

def create_table(engine):
    Base.metadata.create_all(engine)

class Pessoa(Base):
    __tablename__ = 'pessoa'
    __table_args__ = tuple([CheckConstraint("sexo in ('M', 'F')")])

    cpf = Column(Integer, nullable=False, primary_key=True, autoincrement=False)
    cns = Column(Integer, nullable=True, unique=True)
    nome = Column(String(200), nullable=False)
    data_nascimento = Column(Date, nullable=False)
    telefone = Column(String(20), nullable=True)
    sexo = Column(String(1), nullable=True)
    etnia = Column(String(20), nullable=True)
    nome_mae = Column(String(200), nullable=True)

    endereco = relationship('Endereco', back_populates='pessoa', cascade="all, delete", uselist=False)
    vacina = relationship('Vacina', back_populates='pessoa', cascade="all, delete")


class Vacina(Base):
    __tablename__ = 'vacina'

    __table_args__ = tuple([CheckConstraint("dose in (1, 2)")])

    id = Column(Integer, primary_key=True)
    data_de_aplicacao = Column(Date, nullable=False)
    tipo = Column(String(50), nullable=False)
    grupo_alvo = Column(Text, nullable=True)
    lote = Column(Integer, nullable=False)
    dose = Column(Integer, nullable=False)
    vacinador = Column(String(100), nullable=False)
    unidade = Column(String(100), nullable=False)
    
    pessoa = relationship('Pessoa', back_populates='vacina')
    pessoa_cpf = Column(Integer, ForeignKey('pessoa.cpf', ondelete="CASCADE"))


class Endereco(Base):
    __tablename__ = 'endereco'
    
    __table_args__ = tuple([CheckConstraint("zona in ('rural', 'urbana')")])
    
    id = Column(Integer, primary_key=True)
    endereco = Column(String(100), nullable=False)
    bairro = Column(String(50), nullable=True)
    numero = Column(Integer, nullable=True)
    complemento = Column(Text, nullable=True)
    municipio = Column(String(50), nullable=False)
    zona = Column(String(6), nullable=True)

    pessoa = relationship('Pessoa', back_populates='endereco')
    pessoa_cpf = Column(Integer, ForeignKey('pessoa.cpf', ondelete="CASCADE"))
