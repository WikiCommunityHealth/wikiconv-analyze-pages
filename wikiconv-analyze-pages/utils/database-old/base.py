from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql://root:root@localhost:5432/sqlalchemy')
Session = sessionmaker(bind=engine)

Base = declarative_base()



# import psycopg2
# import sqlalchemy as db

# from sqlalchemy import Column, Integer, String
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker

# Base = declarative_base()

# class Product(Base):
#     __tablename__ = 'products'
#     id=Column(Integer, primary_key=True)
#     name=Column(String, primary_key=True)
#     yearmonth=Column(String(6), primary_key=True)
#     m=Column(Integer)


# class DatabaseService:
#     engine: db.engine.Engine

#     def __init__(self) -> None:
#         self.engine = db.create_engine('postgresql://usr:pass@localhost:5432/sqlalchemy')
#         Session = sessionmaker(bind=self.engine)
#         session = Session()


#     def insertMetric(self) -> None:

