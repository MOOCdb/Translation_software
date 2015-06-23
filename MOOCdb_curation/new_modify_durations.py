import MySQLdb
import datetime
import getpass
import time
from sql_functions import *

MAX_DURATION_SECONDS = 3600
DEFAULT_DURATION_SECONDS = 100      # duration if next event is > MAX_DURATION_SECONDS away
BLOCK_SIZE = 50000

def modify_durations(dbName, userName, passwd, host, port):
    connection = openSQLConnectionP(dbName, userName, passwd, host, port)
    cursor = connection.cursor()

    cursor.execute('SELECT DISTINCT(user_id) FROM observed_events')
    user_ids = cursor.fetchall()
    count = 0
    begin = time.time()
    for user_id_tuple in user_ids:
        user_id = user_id_tuple[0]
        #make sure we have index on timestamp (check if index makes it faster)
        last_timestamp = datetime.datetime.fromtimestamp(0).isoformat()
        last_block = False
        while not last_block:
            cursor.execute('''SELECT observed_event_id, observed_event_timestamp
                      FROM observed_events
                      WHERE user_id = '%s'
                      AND observed_event_timestamp >= '%s'
                      ORDER BY observed_event_timestamp
                      LIMIT %s''' % (user_id, last_timestamp, BLOCK_SIZE))
            #last block, add max datetime
            rows = list(cursor.fetchall())
            if len(rows) < BLOCK_SIZE:
                rows.append(('', datetime.datetime.max))
                last_block = True
            for i,row in enumerate(rows[:-1]):
                duration = calc_duration(row[1], rows[i+1][1])
                cursor.execute('''UPDATE observed_events
                            SET observed_event_duration = '%s'
                            WHERE observed_event_id = '%s'
                            ''' % (duration, row[0]))
                connection.commit()
            last_timestamp = rows[-1][1]
        count += 1
        if count == 50:
            print "elapsed time for 50 users: ", time.time() - begin
            begin = time.time()
            count = 0
    cursor.close()
    connection.close()

def calc_duration(timestamp1, timestamp2):
    duration = int((timestamp2 - timestamp1).total_seconds())
    truncated_duration = duration if duration <= MAX_DURATION_SECONDS else DEFAULT_DURATION_SECONDS
    return truncated_duration

