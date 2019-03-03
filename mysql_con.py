import pymysql
import json


def mysql_con(db_name):
    """
    pass in db name, returns mysql connection

    """

    with open('config.json', 'r') as cf:
        config = json.load(cf)
        host = config["config"]["mysql_host"]
        user = config["config"]["mysql_user"]
        pw = config["config"]["mysql_password"]

    conn = pymysql.connect(host=host,
                         user=user,
                         password=pw,
                         db=db_name,
                         charset='utf8mb4',
                         cursorclass=pymysql.cursors.DictCursor)
    return conn
