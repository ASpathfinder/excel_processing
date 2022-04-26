from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy import create_engine

Base = declarative_base()


class Report(Base):
    __tablename__ = 'report'

    code = Column(String(12), primary_key=True)
    parent = Column(String(12), ForeignKey('report.code'))
    name = Column(String(100))
    children = relationship('Report')


engine = create_engine('sqlite://', echo=False)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
