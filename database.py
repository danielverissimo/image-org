from datetime import datetime
import os
from random import randint
import sqlalchemy as sa
import sqlalchemy.orm as orm
from settings import DEBUG, USE_DB, MAIN_STORE_FULL_PATH, DB_DEBUG

# ----------------------- Database Configuration Domain ---------------------- #

INTERNAL_CONNECTION = 'sqlite:///internal.db'
# DB_CONNECTION = 'sqlite:///main.db'
DB_CONNECTION = 'mysql+pymysql://root:fc24m8u3J41W9hcDnkQZLldwJ4i2um3lUa/Ogkm2BHc=@localhost/fotografica'
FILEPATH_LIMIT = 200 # Filepath limit in characters.

InternalModel = orm.declarative_base()
MainModel = orm.declarative_base()

class InputFile(InternalModel):
    __tablename__ = 'input_files'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    absolute_path = sa.Column(sa.String(200))
    proccessed = sa.Column(sa.Boolean())

    def __repr__(self):
        return f'InputFile(id={self.id},absolute_path={self.absolute_path})'

class Camera(MainModel):
    __tablename__ = 'cameras'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    numero = sa.Column(sa.Integer)
    descricao = sa.Column(sa.String(200))
    diretorio = sa.Column(sa.String(200))
    fotografo = sa.Column(sa.String(200))
    created_at = sa.Column(sa.TIMESTAMP)
    updated_at = sa.Column(sa.TIMESTAMP)
    deleted_at = sa.Column(sa.TIMESTAMP)

    def __repr__(self):
        return f'Camera(id={self.id},numero={self.numero},descricao={self.descricao},diretorio={self.diretorio},fotografo={self.fotografo})'

class Foto(MainModel):
    __tablename__ = 'fotos'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    camera_id = sa.Column(sa.BigInteger)
    grupo_id = sa.Column(sa.BigInteger)
    user_id = sa.Column(sa.BigInteger)
    arquivo = sa.Column(sa.String(191))
    created_at = sa.Column(sa.TIMESTAMP)
    updated_at = sa.Column(sa.TIMESTAMP)
    deleted_at = sa.Column(sa.TIMESTAMP)

class Grupo(MainModel):
    __tablename__ = 'grupos'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    codigo = sa.Column(sa.String(191))
    data_impressao = sa.Column(sa.DateTime)
    data_entrega = sa.Column(sa.DateTime)
    created_at = sa.Column(sa.TIMESTAMP)
    updated_at = sa.Column(sa.TIMESTAMP)
    deleted_at = sa.Column(sa.TIMESTAMP)

def internalDb():
    return sa.create_engine(INTERNAL_CONNECTION, echo=DB_DEBUG, future=True)

def mainDb():
    return sa.create_engine(DB_CONNECTION, echo=DB_DEBUG, future=True)

def createInternalTables():
    engine = internalDb()
    InternalModel.metadata.create_all(engine)

def createMainTables():
    engine = mainDb()
    MainModel.metadata.create_all(engine)

def getInternalSession():
    return orm.Session(internalDb())

def getMainSession():
    return orm.Session(mainDb())

# ---------------------------------------------------------------------------- #


# ----------------------------- Repository Domain ---------------------------- #

def getAllProcessedInputFiles():
    with (getInternalSession()) as session:
        stmt = sa.select(InputFile).where(InputFile.proccessed == True)
        objs = []
        for obj in session.execute(stmt):
            objs.append(obj[0])
        return objs

def withoutProcessedPaths(paths):
    if (USE_DB):
        all_processed_inputs = [input.absolute_path for input in getAllProcessedInputFiles()]
        
        return [path for path in paths if not (path in all_processed_inputs)]
    else:
        return paths

def storeProcessedPaths(paths):
    if (USE_DB):
        with (getInternalSession()) as session:
            session.commit()
            for path in paths:
                session.add(InputFile(absolute_path=path, proccessed=True))
            session.commit()

def storeGroup(group, code, camera_id):
    with (getMainSession()) as session:
        session.commit()
        grupo = Grupo(
            codigo=code,
            data_impressao=None,
            data_entrega=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            deleted_at=None
        )
        session.add(grupo)
        session.commit()

        fotos = []

        for [path, img] in group:
            arquivo = path if MAIN_STORE_FULL_PATH else os.path.basename(path)

            foto = Foto(
                camera_id=camera_id,
                grupo_id = grupo.id,
                user_id = 1,
                arquivo = arquivo,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                deleted_at=None
            )
            session.add(foto)

        session.commit()

def getAllCameras():
    with (getMainSession()) as session:
        stmt = sa.select(Camera)
        objs = []
        for obj in session.execute(stmt):
            objs.append(obj)
        return objs