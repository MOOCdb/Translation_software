import MySQLdb
import datetime
import getpass
from sql_functions import *

DATABASES = ["201x_2013_spring",'1473x_2013_spring','203x_2013_3t','3091x_2012_fall','3091x_2013_spring','6002x_fall_2012','6002x_spring_2013']

MAX_DURATION_SECONDS = 3600
DEFAULT_DURATION_SECONDS = 100      # duration if next event is > MAX_DURATION_SECONDS away

def modify_durations(dbName, userName, passwd, host, port):
    print "running databse", dbName
    connection = openSQLConnectionP(dbName, userName, passwd, host, port)
    cursor = connection.cursor()



    for user_id in get_user_id_set(cursor, "observed_events"):
        cursor.execute(" SELECT observed_event_id, observed_event_timestamp" +
                       " FROM " + TABLE +
                       " WHERE user_id = " + fix_id_string(user_id))

        for event_id, calc_duration in calculate_durations(cursor.fetchall()):
            cursor.execute(" UPDATE " + TABLE +
                           " SET observed_event_duration = " + str(calc_duration) +
                           " WHERE observed_event_id = " + fix_id_string(event_id))
            connection.commit()

    print "finished"
    cursor.close()
    connection.close()


def get_user_id_set(cursor, table):
    cursor.execute("SELECT DISTINCT(user_id) FROM " + table)
    return [row[0] for row in cursor.fetchall()]


def fix_id_string(string):
    return "'" + string + "'"


def calculate_durations(event_seq):
    """
    event_seq is a tuple of (event_id, timestamp) tuples
    returns list of (event_id, duration) tuples
    """

    event_seq = sorted(event_seq, key=lambda id_date_pair: id_date_pair[1])
    event_seq.append(("", datetime.datetime.max))
    new_seq = []

    for i in range(len(event_seq) - 1):
        duration = int((event_seq[i + 1][1] - event_seq[i][1]).total_seconds())
        truncated_duration = duration if duration <= MAX_DURATION_SECONDS else DEFAULT_DURATION_SECONDS
        new_seq.append((event_seq[i][0], truncated_duration))

    return new_seq
