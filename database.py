from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

URL_DATABASE =os.getenv('URL_DATABASE')

engine = create_engine(URL_DATABASE)

sessionLocal = sessionmaker(autoflush=False, bind=engine, autocommit=False)

Base= declarative_base()

