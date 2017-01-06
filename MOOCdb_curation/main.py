import sql_functions
import getpass
import os

#curation
# import modify_durations as md
import new_modify_durations as md
import resources as res
import submissions as sub
import observed_events as obv
'''

Author : Sebastien Boyer

Pre-processing database before feature extraction


'''

def curate(dbName = None, userName=None, passwd=None, dbHost=None, dbPort=None,
        startDate=None):

    if not dbName:
        dbName = '3091x_2013_spring'
    if not userName:
        userName = 'sebboyer'
    if not passwd:
        passwd = getpass.getpass()
    if not dbHost:
        dbHost = 'alfa6.csail.mit.edu'
    if not dbPort:
        dbPort = 3306
    if not startDate:
        startDate='2013-04-09 00:00:00'


    # fileName, wordsToBeReplaced, wordsToReplace
    # preprocessing_files = [
    sql_files_to_run = [

        # [
        #  'initial_preprocessing.sql',
        #  ['moocdb'],
        #  [dbName]
        # ],
        # [
        #  'add_submissions_validity_column.sql',
        #  ['moocdb'],
        #  [dbName]
        # ],
        # [
        #  'problems_populate_problem_week.sql',
        #  ['2013-09-24 13:14:07','moocdb'],
        #  [startDate,dbName]
        # ],
        [
         'users_populate_user_last_submission_id.sql',
         ['INT(11)','moocdb'],
         ['VARCHAR(50)',dbName]
        ]

    ]

    # SQL files
    run_sql_curation_files(dbName, userName, passwd, dbHost, dbPort,
           sql_files_to_run)

    # Python files

    #Recalculate Durations
    print "Recalculating durations"
        #-durations were originally calculated wrong in observed_events
        #this fixes that
        #takes a long time (~3-4 hours per db)
    # md.modify_durations(dbName, userName, passwd, dbHost, dbPort)
    print "done"

    print "Curating database:"

    print "curating submissions table"
    # sub.curate_submissions(dbName, userName, passwd, dbHost, dbPort)
    print "done"

    print "Curating observed events table"
    #minimum duration for observed_events table:
    min_time = 10
    # obv.curate_observed_events(dbName, userName, passwd, dbHost, dbPort, min_time)
    print "done"

    print "Curating resource table"
    # res.populate_resource_type(dbName, userName, passwd, dbHost, dbPort)
    print "done"



def run_sql_curation_files(dbName, userName, passwd, dbHost, dbPort,preprocessing_files):
    conn = sql_functions.openSQLConnectionP(dbName, userName, passwd, dbHost,dbPort)

    for fileName, toBeReplaced, replaceBy in preprocessing_files:
        fileLocation = os.path.dirname(os.path.realpath(__file__))+'/'+ fileName
        print fileLocation
        newFile = sql_functions.replaceWordsInFile(fileLocation, toBeReplaced, replaceBy)
        print "executing: ", fileName
        sql_functions.executeSQL(conn, newFile)
        conn.commit()
        print "done"

    sql_functions.closeSQLConnection(conn)

def run_curation_all(userName=None, passwd = None, dbs = None, dbHost = None,
        dbPort = None, startDates = None):
    if not userName:
        userName = 'sebboyer'
    if not passwd:
        passwd = getpass.getpass()
    if not dbs:
        dbs = ['201x_2013_spring','1473x_2013_spring', '203x_2013_3t',
               '3091x_2012_fall','3091x_2013_spring',
               '6002x_fall_2012','6002x_spring_2013']
    if not startDates:
        #these dates are wrong, but just an example
        startDates = ['2012-03-05 12:00:00']*len(dbs)
    if not dbHost:
        dbHost = 'alfa6.csail.mit.edu'
    if not dbPort:
        dbPort = 3306

    for i,db in enumerate(dbs):
        print "curating ", db
        curate(db, userName, passwd, 'alfa6.csail.mit.edu', 3306, startDates[i])

if __name__ == "__main__":
    #run_curation_all()
    # curate(dbName = '201x_2013_spring')
    curate(dbName             = 'moocdb',
         userName           = 'root',
         # passwd
         dbHost             = 'localhost',
         # dbPort
         #This date is year-month-day
         startDate         = '2013-09-24 13:14:07', # last date is 2014-03-11 05:09:03
        )
