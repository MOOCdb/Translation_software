import MySQLdb
import datetime
import getpass
import time
from sql_functions import *
import csv
import os
import glob
import numpy as np


######################################## MODIFY DURATIONS ###############################################

def modify_durations(connection,MAX_DURATION_SECONDS = 3600,DEFAULT_DURATION_SECONDS = 100,BLOCK_SIZE = 50000):
    # DEFAULT_DURATION_SECONDS is duration if next event is > MAX_DURATION_SECONDS away
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
                duration = calc_duration(row[1], rows[i+1][1],MAX_DURATION_SECONDS,DEFAULT_DURATION_SECONDS,BLOCK_SIZE)
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
    # connection.close()

def calc_duration(timestamp1, timestamp2,MAX_DURATION_SECONDS,DEFAULT_DURATION_SECONDS,BLOCK_SIZE):
    duration = int((timestamp2 - timestamp1).total_seconds())
    truncated_duration = duration if duration <= MAX_DURATION_SECONDS else DEFAULT_DURATION_SECONDS
    return truncated_duration


######################################## CURATE OBSERVED EVENTS ###############################################

def curate_observed_events(conn,min_time = 10,BLOCK_SIZE=50):
    # conn = openSQLConnectionP(dbName, userName, passwd, host, port)
    #cursor = conn.cursor()
    ## invalidate events with duration less than min_time
    #invalidate_durations = '''
        #UPDATE observed_events
        #SET validity = 0
        #WHERE observed_event_duration < '%s'
    #''' % (min_time)
    #cursor.execute(invalidate_durations)
    #conn.commit()
    #cursor.close()

    cursor = conn.cursor()

    # invalidate consecutive repeated events
    # defined as consecutive events with same timestamp
    # AND same duration AND same user_id
    select_potential_events = '''
        SELECT  e.user_id, e.observed_event_timestamp, e.observed_event_duration, e.observed_event_id
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

    modify_valids = '''
        UPDATE observed_events
        SET validity = 1
        WHERE observed_event_id in (%s)
    '''
    # Alec edit - fix valid_event_ids list by casting to int
    valid_event_ids = [int(s) for s in valid_event_ids]

    block_sql_command(conn, cursor, modify_valids, valid_event_ids, BLOCK_SIZE)

    cursor.close()
    cursor = conn.cursor()

    if len(invalid_event_ids) > 0:
        modify_invalids = '''
            UPDATE observed_events
            SET validity = 0
            WHERE observed_event_id in (%s)
        '''
        # Alec edit - fix invalid_event_ids list by casting to int
        invalid_event_ids = [int(s) for s in invalid_event_ids]
        
        block_sql_command(conn, cursor, modify_invalids, invalid_event_ids, BLOCK_SIZE)

        cursor.close()

    # conn.close()

def events_equal(row1, row2):
    # 0 = user_id
    # 1 = timestamp
    # 2 = duration
    for i in range(3):
        if row1[i] != row2[i]:
            return False
    return True



######################################## CURATE RESOURCES ###############################################

def extract_NumberEnrollments(conn):
    txt='Select count(distinct user_id) from observed_events'
    cursor = conn.cursor()
    cursor.execute(txt)
    c = cursor.fetchone()
    cursor.close()
    if c:
        c = c[0][0]
    return c

# Test if string contains word in it
def string_contains_word(string,word):
    l_word=len(word)
    l=len(string)
    instance=0
    i=0
    while len(string[i:l])-l_word>-1:
        if string[i:i+l_word]==word:
           instance+=1
        i+=1
    return instance>0

# Return the list of the resource_type_names in order of appearance in resource_types table
def extract_resource_types(conn):
    command='select resource_type_id,resource_type_name from resource_types;'
    cursor = conn.cursor()
    cursor.execute(command)
    c = cursor.fetchall()
    cursor.close()
    res_types=[]
    if c:
        for i in range(len(c)):
            res_types.append(c[i][1])
    return res_types

# Return the resource_type_id (=index in the list of resource_type_names) corresponding to a url
# and 0 if the url does not match any resource_type names
def compute_resource_type_id(res_types,url):
    result=0
    for x in res_types:
        if string_contains_word(url,x):
            result=res_types.index(x)
    return result


# Populate the resource_type_id for the resources having resource_type_id=0
# when uri matches one of the resource_type_names in the resource_types table
def populate_resource_type(conn):

    # conn = openSQLConnectionP(dbName, userName, passwd, host, port)
    # Extract resources types of the database
    res_types=extract_resource_types(conn)

    # Fetching the resource_uri's lacking resource_type_id
    command='select resource_id,resource_uri from resources where resource_type_id=0;'
    cursor = conn.cursor()
    cursor.execute(command)
    c = cursor.fetchall()
    cursor.close()

    # Creating a list of all resource_type_id corresponding in order
    ids=[]
    if c:
        for i in range(len(c)):
            ids.append([c[i][0],compute_resource_type_id(res_types,c[i][1])])

    # Updating data base
    cur = conn.cursor()
    count=0
    for i in range(len(ids)):
        res_id=ids[i][0]
        res_type_id=ids[i][1]
        command='update resources set resource_type_id=%s where resource_id=%s' %(res_type_id,res_id)
        conn.commit()
        cur.execute(command)
        count+=1
    closeSQLConnection(conn)

    print "%s rows have been updated" %(count)

    return 0


######################################## CURATE SUBMISSIONS ###############################################

def curate_submissions(conn,dbName,BLOCK_SIZE = 50):
    """
    Created: 5/24/2015 by Ben Schreck

    Curates submissions (and indirectly assessments)
    """

    # conn = openSQLConnectionP(dbName, userName, passwd, host, port)
    cursor = conn.cursor()

    invalidate_submissions_first_pass = '''
        UPDATE `%s`.submissions
        SET validity = 0
        WHERE submission_attempt_number < 0
        OR   submission_is_submitted != 1
    ''' % (dbName)
    cursor.execute(invalidate_submissions_first_pass)
    conn.commit()
    cursor.close()
    cursor = conn.cursor()


    potential_submissions_query= '''
    SELECT  s.submission_id,
            s.user_id,
            s.problem_id,
            s.submission_timestamp,
            s.submission_answer,
            s.submission_attempt_number,
            s.submission_is_submitted,
            a.assessment_grade

    FROM `%s`.submissions AS s
    LEFT JOIN `%s`.assessments AS a
    ON s.submission_id = a.submission_id
    WHERE s.submission_attempt_number > -1
    AND   s.submission_is_submitted = 1
    ORDER BY s.user_id,
             s.problem_id,
             s.submission_attempt_number,
             s.submission_timestamp
             ASC
    ''' % (dbName, dbName)
    cursor.execute(potential_submissions_query)
    data = cursor.fetchall()
    cursor.close()
    cursor = conn.cursor()


    submission_id, user_id, problem_id, timestamp, \
    answer, attempt_number, is_submitted, grade = data[0]


    invalid_submissions= []

    valid_submissions = {user_id: {
                                problem_id: [(submission_id,answer,attempt_number,grade,timestamp)]
                        }}

    for i in range(1,len(data)):
        submission_id, user_id, problem_id, timestamp, \
        answer, attempt_number, is_submitted, grade = data[i]


        if user_id in valid_submissions:
            if problem_id in valid_submissions[user_id]:
                subs = valid_submissions[user_id][problem_id]
                # correct answer
                correct = [1 for x in subs if x[3] == 1]
                #if there is a correct answer already
                #don't include our current submission
                current_is_valid = True
                if len(correct) == 0:
                    current_is_valid = False
                #if our current submission is a duplicate,
                #don't include it
                #duplicate means user_id, problem_id, timestamps identical
                #if current submission is same answer as previous, don't
                #include it

                #previous submission has same answer
                if subs[-1][1] == answer:
                    current_is_valid = False
                if current_is_valid:
                    for sub in subs:
                        #timestamps identical
                        if sub[-1] == timestamp:
                            current_is_valid = False
                if current_is_valid:
                    #user_id, problem_id, timestamp identical
                    valid_submissions[user_id][problem_id].append((submission_id,answer,attempt_number,grade,timestamp))
                else:
                    invalid_submissions.append(submission_id)
            else:
                valid_submissions[user_id][problem_id] = [(submission_id,answer,attempt_number,grade,timestamp)]
        else:
            valid_submissions[user_id] = {problem_id: [(submission_id,answer,attempt_number,grade,timestamp)]}


    # Modify invalid submissions in sql
    modify_invalids = '''
        UPDATE submissions
        SET validity = 0
        WHERE submission_id in (%s)'''
    # Alec edit - fix invalid_submissions list by casting to int
    invalid_submissions = [int(s) for s in invalid_submissions]

    block_sql_command(conn, cursor, modify_invalids, invalid_submissions,BLOCK_SIZE)

    cursor.close()
    cursor = conn.cursor()

    # Modify valid submissions in sql
    valid_submission_ids = []
    for user_id in valid_submissions:
        for problem_id in valid_submissions[user_id]:
            for sub in valid_submissions[user_id][problem_id]:
                valid_submission_ids.append(sub[0])

    modify_valids = '''
        UPDATE submissions
        SET validity = 1
        WHERE submission_id in (%s)
    '''
    # Alec edit - fix valid_submission_ids list by casting to int
    valid_submission_ids = [int(s) for s in valid_submission_ids]
    
    block_sql_command(conn, cursor, modify_valids, valid_submission_ids,BLOCK_SIZE)

    cursor.close()
    # conn.close()


