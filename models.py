from sqlalchemy import create_engine, Column, Table, ForeignKey, MetaData
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (BigInteger, Integer, String, Date, DateTime, Float, Boolean, Text)
from sqlalchemy.sql.schema import CheckConstraint
import logging

Base = declarative_base()

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

class Pessoa(Base):
    __tablename__ = 'pessoa'
    __table_args__ = tuple([CheckConstraint("sexo in ('M', 'F')")])

    cpf = Column(BigInteger, nullable=False, primary_key=True, autoincrement=False)
    cns = Column(BigInteger, nullable=True, unique=True)
    nome = Column(String(200), nullable=False)
    idade = Column(Integer, nullable=True)
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
    nome = Column(String(50), nullable=True)
    tipo = Column(String(50), nullable=False)
    grupo_alvo = Column(Text, nullable=True)
    lote = Column(BigInteger, nullable=False)
    dose = Column(Integer, nullable=True)
    vacinador = Column(String(100), nullable=True)
    unidade = Column(String(100), nullable=False)
    
    pessoa = relationship('Pessoa', back_populates='vacina')
    pessoa_cpf = Column(BigInteger, ForeignKey('pessoa.cpf', ondelete="CASCADE"))


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
    pessoa_cpf = Column(BigInteger, ForeignKey('pessoa.cpf', ondelete="CASCADE"))
