from excel import load_excel
from orm import Session, Report
import pandas as pd


def save(df):
    df = df.where(pd.notnull(df), None)

    records = df.to_dict('records')

    session = Session()

    session.add_all([Report(**record) for record in records])

    session.commit()
