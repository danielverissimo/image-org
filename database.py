import sqlalchemy as sa
import sqlalchemy.orm as orm
from settings import DEBUG, USE_DB

# ----------------------- Database Configuration Domain ---------------------- #

INTERNAL_CONNECTION = 'sqlite:///internal.db'
DB_CONNECTION = 'sqlite:///main.db'
FILEPATH_LIMIT = 200 # Filepath limit in characters.

InternalModel = orm.declarative_base()

class InputFile(InternalModel):
    __tablename__ = 'input_files'
    id = sa.Column(sa.Integer, primary_key=True)
    absolute_path = sa.Column(sa.String(200))
    proccessed = sa.Column(sa.Boolean())

    def __repr__(self):
        return f'InputFile(id={self.id},absolute_path={self.absolute_path})'

def internalDb():
    return sa.create_engine(INTERNAL_CONNECTION, echo=DEBUG, future=True)

def mainDb():
    return sa.create_engine(DB_CONNECTION, echo=DEBUG, future=True)

def createInternalTables():
    engine = internalDb()
    InternalModel.metadata.create_all(engine)

def getInternalSession():
    return orm.Session(internalDb())

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