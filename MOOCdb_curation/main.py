import sql_functions
import getpass
import os
from sql_functions import *

import curate as cu

'''
Author : Sebastien Boyer

Pre-processing database before feature extraction

'''

def curate(dbName = None, userName=None, passwd=None, dbHost=None, dbPort=None,
        startDate=None):

    # Establish connection
    connection = openSQLConnectionP(dbName, userName, passwd, dbHost, dbPort)

    ####### SQL files ########
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
         'users_populate_user_last_submission_id.sql',
         ['INT(11)','moocdb'],
         ['VARCHAR(50)',dbName]
        ]

    ]

    cu.run_sql_curation_files(connection,sql_files_to_run)

    ###### Python files ########

    print "Recalculating durations"
    # durations were originally calculated wrong in observed_events, this fixes that, takes a long time (~3-4 hours per db)
    cu.modify_durations(connection)
    print "done"

    print "Curating database:"

    print "curating submissions table"
    cu.curate_submissions(connection,dbName)
    print "done"

    print "Curating observed events table"
    cu.curate_observed_events(connection)
    print "done"

    print "Curating resource table"
    cu.populate_resource_type(connection)
    print "done"


if __name__ == "__main__":
    curate(dbName             = 'moocdb',
         userName           = 'root',
         passwd             = getpass.getpass(),
         dbHost             = 'localhost',
         dbPort             = 3306,
         startDate         = '2013-09-24 13:14:07'
        )
