import os
import json
import psycopg2
from ast import literal_eval

def backup(file=None):
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    if file!=None:
        with open(file) as json_file:
            data = json.load(json_file)
        cursor = conn.cursor()
        delete_query="""DELETE FROM json WHERE name = '{name}'""".format(name=file)
        insert_query="""INSERT INTO json (NAME, VALUE) VALUES (%s, %s)"""
        record_to_insert = (file, json.dumps(data))
        cursor.execute(delete_query)
        cursor.execute(insert_query, record_to_insert)
        conn.commit()
        cursor.close()
        return
    json_files = ['leaderboard.json']
    for backup_file in json_files:
        with open(backup_file) as json_file:
            data = json.load(json_file)
        cursor = conn.cursor()
        delete_query="""DELETE FROM json WHERE name = '{name}'""".format(name=backup_file)
        insert_query="""INSERT INTO json (NAME, VALUE) VALUES (%s, %s)"""
        record_to_insert = (backup_file, json.dumps(data))
        cursor.execute(delete_query)
        cursor.execute(insert_query, record_to_insert)
        conn.commit()
        cursor.close()
    conn.close()


def restore(file=None):
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    if file!=None:
        cursor = conn.cursor()
        select_query="""SELECT VALUE FROM json WHERE name = '{}'""".format(file)
        cursor.execute(select_query)
        data = cursor.fetchall()
        conn.commit()
        cursor.close()
        data=str(data)[2:-3]
        data=literal_eval(data)
        return data
    json_files = ['leaderboard.json']
    for restore_file in json_files:
        cursor = conn.cursor()
        select_query="""SELECT VALUE FROM json WHERE name = '{}'""".format(restore_file)
        cursor.execute(select_query)
        data = cursor.fetchall()
        conn.commit()
        cursor.close()
        try:
            data=str(data)[2:-3]
            data=literal_eval(data)
            with open(restore_file, 'w') as json_file:
                json.dump(data, json_file)
        except:
            pass
    conn.close()
