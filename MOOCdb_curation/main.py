import sql_functions
import getpass
import os
from sql_functions import *

import curation as cu

'''

Author : Sebastien Boyer

Pre-processing database before feature extraction


'''

def curate(dbName = None, userName=None, passwd=None, dbHost=None, dbPort=None,
        startDate=None):

    # Establish connection
    connection = openSQLConnectionP(dbName, userName, passwd, dbHost, dbPort)

    sql_files_to_run = [

        # [
        #  'initial_preprocessing.sql',
        #  ['moocdb'],
        #  [dbName]
        # ],
        [
         'add_submissions_validity_column.sql',
         ['moocdb'],
         [dbName]
        ],
        [
         'problems_populate_problem_week.sql',
         ['2013-09-24 13:14:07','moocdb'],
         [startDate,dbName]
        ],
        [
         'alec_users_populate_user_last_submission_id.sql',
         ['INT(11)','moocdb'],
         ['VARCHAR(50)',dbName]
        ]

    ]

    # SQL files
    cu.run_sql_curation_files(connection,sql_files_to_run)

    # Python files
    # dbName, userName, passwd, host, port, 

    #Recalculate Durations
    print "Recalculating durations"
        #-durations were originally calculated wrong in observed_events
        #this fixes that
        #takes a long time (~3-4 hours per db)
    cu.modify_durations(connection)
    # cu.modify_durations(dbName, userName, passwd, dbHost, dbPort)
    print "done"

    print "Curating database:"

    print "curating submissions table"
    cu.curate_submissions(connection,dbName)
    # cu.curate_submissions(dbName, userName, passwd, dbHost, dbPort)
    print "done"

    print "Curating observed events table"
    #minimum duration for observed_events table:
    # min_time = 10
    cu.curate_observed_events(connection)
    # cu.curate_observed_events(dbName, userName, passwd, dbHost, dbPort, min_time)
    print "done"

    print "Curating resource table"
    cu.populate_resource_type(connection)
    # cu.populate_resource_type(dbName, userName, passwd, dbHost, dbPort)
    print "done"


if __name__ == "__main__":
    #run_curation_all()
    # curate(dbName = '201x_2013_spring')
    curate(dbName             = 'moocdb',
         userName           = 'root',
         passwd             = getpass.getpass(),
         dbHost             = 'localhost',
         dbPort             = 3306,
         #This date is year-month-day
         startDate         = '2013-09-24 13:14:07', # last date is 2014-03-11 05:09:03
        )
