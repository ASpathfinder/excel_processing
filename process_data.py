from orm import Session, Report
from excel import load_excel
from save_to_db import save
import datetime
import pandas as pd
import os


def analyze(df):
    session = Session()

    #first step
    codes_from_new_excel = set([code.strip() for code in df.code.to_list()])

    reports = session.query(Report).all()
    system_report_codes = set([report.code[2:-1] for report in reports])

    first_rslt_df = df[df['code'].isin(codes_from_new_excel - system_report_codes)]

    # second step

    new_reports_parents = set(['20{}'.format(parent.strip()) for parent in first_rslt_df.parent.to_list()])

    system_parent_reports = session.query(Report).filter(Report.code.like('%7')).all()
    system_parents = set([report.code.strip() for report in system_parent_reports])


    second_rslt_df_exists_in_system = first_rslt_df[first_rslt_df['parent'].isin(
        [parent[2:] for parent in list(new_reports_parents & system_parents)]
    )]

    second_rslt_df_not_exists_in_system = first_rslt_df[first_rslt_df['parent'].isin(
        [parent[2:] for parent in list(new_reports_parents - system_parents)]
    )]

    def apply(row):
        print(row)
        row['name'] = row['name'].strip()
        if row['parent'] != '0':
            row['parent'] = '20{}'.format(row['parent'])
        if row['type'].strip() == '叠加汇总表':
            row['code'] = '20{}7'.format(row['code'])
        elif row['type'].strip() == '单户表':
            row['code'] = '20{}0'.format(row['code'])
        return row

    second_rslt_df_exists_in_system = second_rslt_df_exists_in_system.apply(apply, axis=1)
    second_rslt_df_not_exists_in_system = second_rslt_df_not_exists_in_system.apply(apply, axis=1)

    os.makedirs('output', exist_ok=True)
    with pd.ExcelWriter('output/second_result_{:%Y-%m-%d_%H%M%S}.xls'.format(datetime.datetime.now()), engine='xlsxwriter') as writer:
        second_rslt_df_exists_in_system.to_excel(writer, sheet_name='父节点存在于系统', columns=['name', 'code', 'parent'], index=False)
        second_rslt_df_not_exists_in_system.to_excel(writer, sheet_name='父节点不存在于系统', columns=['name', 'code', 'parent'], index=False)


def analyze_2(df):
    session = Session()

    # first step
    codes_from_new_excel = set([code.strip() for code in df.code.to_list()])

    reports = session.query(Report).all()

    system_report_codes = set([report.code.strip() for report in reports])

    first_rslt_df = df[df['code'].isin(codes_from_new_excel - system_report_codes)]

    # second step

    new_reports_parents = set([parent.strip() for parent in first_rslt_df.parent.to_list()])

    system_parent_reports = session.query(Report).filter(Report.code.like('%7')).all()

    system_parents = set([report.code.strip() for report in system_parent_reports])

    second_rslt_df_exists_in_system = first_rslt_df[first_rslt_df['parent'].isin(
        [parent[2:] for parent in list(new_reports_parents & system_parents)]
    )]

    second_rslt_df_not_exists_in_system = first_rslt_df[first_rslt_df['parent'].isin(
        [parent[2:] for parent in list(new_reports_parents - system_parents)]
    )]

    first_rslt_df.to_excel('output/湖州.xls', engine='xlsxwriter', index=False)


if __name__ == '__main__':
    df = load_excel(
        io='files/2021年内控报告.xls',
        names=['code', 'name', 'parent'],
        usecols='A:C',
    )

    save(df)

    df = load_excel(
        io='files/21年度树形不含宁波(1).XLS',
        names=['name', 'code', 'type', 'parent'],
        usecols='A,B,C,D',
    )

    analyze(df)


