import pymysql
import json


def mysql_con():

    with open('config.json', 'r') as cf:
        config = json.load(cf)
        host = config["config"]["mysql_host"]
        user = config["config"]["mysql_user"]
        pw = config["config"]["mysql_password"]

    conn = pymysql.connect(host=host,
                         user=user,
                         password=pw,
                         db='Dev',
                         charset='utf8mb4',
                         cursorclass=pymysql.cursors.DictCursor)
    return conn
