from excel import load_excel
from util import check_str
import pandas as pd
import numpy as np
import re


def generate_orm(df, tablename=''):
    orm_strs = []
    unique_cols = []
    primary_cols = []
    for item in df.to_dict('records'):
        col_type = 'String'
        col_len = int(item['字段长度']) if all([item['字段长度'] is not None, item['字段长度'] is not np.nan]) else None
        col_type_len = "({})".format(col_len) if col_len else ''
        index = ""
        primary = ""
        unique = ""
        default = ""
        auto_increment = ""
        doc = item['备注描述'].strip() if item['备注描述'] else ''
        if check_str(item['键约束']) == '索引键':
            index = 'index=True'
        elif check_str(item['键约束']) == '主键':
            primary = 'primary_key=True'
        elif check_str(item['键约束']) == '联合主键':
            primary = 'primary_key=True'
            primary_cols.append("'{}'".format(item['字段名称']))

        if check_str(item['唯一约束']) == '单字段':
            unique = 'unique=True'
        elif check_str(item['唯一约束']) == '多字段':
            unique_cols.append("'{}'".format(item['字段名称']))

        if check_str(item['默认值']) == '自增':
            auto_increment = "autoincrement=True"
        elif check_str(item['默认值']):
            default = "server_default=text(\"'{}'\")".format(item['默认值'])

        chains = []
        if auto_increment:
            chains.append(auto_increment)
        if any([index, primary]):
            chains.append(index if index else primary)
        if default:
            chains.append(default)
        if unique:
            chains.append(unique)

        if item['字段类型'].lower() == 'int':
            col_type = 'Integer{}'.format(col_type_len)
        elif item['字段类型'].lower() in ['string', 'varchar']:
            col_type = 'String{}'.format(col_type_len)
        elif item['字段类型'].lower() == 'decimal':
            col_type = 'DECIMAL{}'.format(col_type_len)
        elif item['字段类型'].lower() == 'datetime':
            col_type = 'DateTime'

        orm_col = "{0} = Column('{0}', {1}, nullable=False, {2}comment='{3}', doc=\"{4}\")".format(
            item['字段名称'],
            col_type,
            ', '.join(chains) + ', ' if chains else '',
            item['字段名称（中文）'],
            doc
            )

        orm_strs.append(orm_col)

    if tablename:
        print("__tablename__='{}'".format(tablename))

    unique_constraint = ''
    if len(unique_cols) >= 2:
        unique_constraint = "UniqueConstraint({0}name='{1}_m_uq_constraint')".format(', '.join(unique_cols) + ', ', tablename)

    primary_constraint = ''
    if len(primary_cols) >= 2:
        primary_constraint = "PrimaryKeyConstraint({0}name='{1}_m_pk_constraint')".format(', '.join(primary_cols) + ', ', tablename)

    constraints = []
    if unique_constraint:
        constraints.append(unique_constraint)
    if primary_constraint:
        constraints.append(primary_constraint)

    if constraints:
        table_args = """
    __table_args__ = (
        {},
    )
        """.format(',\n'.join(constraints))

        print(table_args)
    else:
        print('')

    for col in orm_strs:
        print(col)


if __name__ == '__main__':
    file = 'files/data_collection/桥梁检测数据相关表设计.xlsx'
    sheet = '桥梁检测构件检测记录-媒体数据'

    df = load_excel(
        io=file,
        usecols='C:M',
        skiprows=1,
        nrows=12,
        sheet_name=sheet
    )

    df1 = df.replace({np.nan: None})
    print(df1)

    df_2 = load_excel(
        io=file,
        usecols='A',
        nrows=1,
        sheet_name=sheet
    )

    generate_orm(df1, tablename=re.search(r'（(.+)）', list(df_2.to_dict('records')[0].keys())[0]).group(1))
