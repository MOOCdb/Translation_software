"""
Created: 5/24/2015 by Ben Schreck

Curates observed events
"""

import MySQLdb
import time
import csv
import os
import glob
from sql_functions import *
import getpass

def curate_observed_events(dbName, userName, passwd, host, port, min_time = 10):
    conn = openSQLConnectionP(dbName, userName, passwd, host, port)
    cursor = conn.cursor()
    # invalidate events with duration less than min_time
    invalidate_durations = '''
        UPDATE observed_events
        SET validity = 0
        WHERE observed_event_duration < '%s'
    ''' % (min_time)
    cursor.execute(invalidate_durations)
    cursor.close()

    cursor = conn.cursor()

    # invalidate consecutive repeated events
    # defined as consecutive events with same timestamp AND same resource id AND same duration
    # also currently same user_id. is that right?
    select_potential_events = '''
        SELECT  e.user_id, e.observed_event_timestamp, e.url_id, e.observed_event_duration, e.observed_event_id
        FROM observed_events as e
        WHERE observed_event_duration >= '%s'
        ORDER BY e.user_id, e.observed_event_timestamp ASC
    ''' % (min_time)
# Do we need this?
#        INNER JOIN urls as u
#         ON u.url_id = e.url_id
    cursor.execute(select_potential_events)
    data = cursor.fetchall()
    cursor.close()
    cursor = conn.cursor()

    valid_event_ids = [data[0][-1]]
    invalid_event_ids = []
    for i in range(1,len(data)):
        if events_equal(data[i], data[i-1]):
            invalid_event_ids.append(data[i][-1])
        else:
            valid_event_ids.append(data[i][-1])

    sub_id_str = str(valid_event_ids)[1:-1]
    modify_valids = '''
        UPDATE observed_events
        SET validity = 1
        WHERE observed_event_id in (%s)
    ''' % (sub_id_str)
    cursor.execute(modify_valids)
    cursor.close()
    cursor = conn.cursor()

    if len(invalid_event_ids) > 0:
        sub_id_str = str(invalid_event_ids)[1:-1]
        modify_invalids = '''
            UPDATE observed_events
            SET validity = 0
            WHERE observed_event_id in (%s)
        ''' % (sub_id_str)
        print modify_invalids[:2000]
        cursor.execute(modify_invalids)
        cursor.close()

    conn.commit()
    conn.close()

def events_equal(row1, row2):
    # 0 = user_id
    # 1 = timestamp
    # 2 = url_id
    # 3 = duration
    for i in range(4):
        if row1[i] != row2[i]:
            return False
    return True
