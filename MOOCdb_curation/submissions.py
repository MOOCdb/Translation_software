"""
Created: 5/24/2015 by Ben Schreck

Curates submissions (and indirectly assessments)
"""

import MySQLdb
import time
import csv
import os
import glob
from sql_functions import *
import getpass

BLOCK_SIZE = 50

def curate_submissions(dbName, userName, passwd, host, port):
    conn = openSQLConnectionP(dbName, userName, passwd, host, port)
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
    block_sql_command(conn, cursor, modify_valids, valid_submission_ids,BLOCK_SIZE)

    cursor.close()
    conn.close()
