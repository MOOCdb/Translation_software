import MySQLdb
import datetime
import getpass
from sql_functions import *
import time

DATABASES = ["201x_2013_spring",'1473x_2013_spring','203x_2013_3t','3091x_2012_fall','3091x_2013_spring','6002x_fall_2012','6002x_spring_2013']

MAX_DURATION_SECONDS = 3600
DEFAULT_DURATION_SECONDS = 100      # duration if next event is > MAX_DURATION_SECONDS away

def modify_durations(dbName, userName, passwd, host, port):
    print "running databse", dbName
    connection = openSQLConnectionP(dbName, userName, passwd, host, port)
    cursor = connection.cursor()


    count = 0
    begin = time.time()
    for user_id in get_user_id_set(cursor, "observed_events"):
        cursor.execute(" SELECT observed_event_id, observed_event_timestamp" +
                       " FROM observed_events" +
                       " WHERE user_id = " + fix_id_string(str(user_id)))

        for event_id, calc_duration in calculate_durations(cursor.fetchall()):
            # cursor.execute(" UPDATE observed_events"+
            #                " SET observed_event_duration = " + str(calc_duration) +
            #                " WHERE observed_event_id = " + fix_id_string(event_id))
            cursor.execute(" UPDATE observed_events"+
                           " SET observed_event_duration = " + str(calc_duration) +
                           " WHERE observed_event_id = " + fix_id_string(str(event_id))) # Alec edit 12/28/2016
            connection.commit()
        count += 1
        if count == 50:
            print "elapsed time for 50 users: ", time.time() - begin
            begin = time.time()
            count = 0

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


#timestamp to durations:
#1 for each user:
#2   events = get all (observed_event_id, observed_event_timestamp)
#3.  sort events by timestamp
#4.  add to last element of array the largest possible timestamp
#5.  from 0 to n-1:
#6.    duration is length from ith timestamp to i+1 timestemp
#7.    if duration > max_duration:
#8.       duration = default duration
#9.   append id, duration to new list

#tried modifying above code to increase performance, but didn't significantly
#affect it
#def modify_durations(dbName, userName, passwd, host, port):
    #connection = openSQLConnectionP(dbName, userName, passwd, host, port)
    #cursor = connection.cursor()

    #cursor.execute('SELECT DISTINCT(user_id) FROM observed_events')
    #user_ids = cursor.fetchall()
    #count = 0
    #begin = time.time()
    #for user_id_tuple in user_ids:
        #user_id = user_id_tuple[0]
        ##make sure we have index on timestamp (check if index makes it faster)
        #last_timestamp = datetime.datetime.fromtimestamp(0).isoformat()
        #last_block = False
        #while not last_block:
            #cursor.execute('''SELECT observed_event_id, observed_event_timestamp
                      #FROM observed_events
                      #WHERE user_id = '%s'
                      #AND observed_event_timestamp >= '%s'
                      #ORDER BY observed_event_timestamp
                      #LIMIT %s''' % (user_id, last_timestamp, BLOCK_SIZE))
            ##last block, add max datetime
            #rows = list(cursor.fetchall())
            #if len(rows) < BLOCK_SIZE:
                #rows.append(('', datetime.datetime.max))
                #last_block = True
            #for i,row in enumerate(rows[:-1]):
                #duration = calc_duration(row[1], rows[i+1][1])
                #cursor.execute('''UPDATE observed_events
                            #SET observed_event_duration = '%s'
                            #WHERE observed_event_id = '%s'
                            #''' % (duration, row[0]))
                #connection.commit()
            #last_timestamp = rows[-1][1]
        #count += 1
        #if count == 50:
            #print "elapsed time for 50 users: ", time.time() - begin
            #begin = time.time()
            #count = 0
    #cursor.close()
    #connection.close()

#def calc_duration(timestamp1, timestamp2):
    #duration = int((timestamp2 - timestamp1).total_seconds())
    #truncated_duration = duration if duration <= MAX_DURATION_SECONDS else DEFAULT_DURATION_SECONDS
    #return truncated_duration

