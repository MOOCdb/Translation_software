'''
Created on 17 sept. 2014

@author: Seb
'''

import MySQLdb
import numpy as np

dbName='DATABASE_YOU_WANT_TO_ACCESS'
extract_MainInfo # Will create a .txt file named "Global report on "+ dbName containing general information about the content of the data base

def executeAndReturn_cursor(databaseName,command):# command of type string and contain an appropriate sql command
    conn = MySQLdb.connect(host='alfa6.csail.mit.edu', port=3306, user='YOUR_USER_NAME', passwd='YOUR_PASSWORD', db=databaseName)
    cur = conn.cursor()
    cur.execute(command)
    conn.close()
    return cur.fetchall()

def executeAndReturn_cursor_txtSQLcommand(databaseName,Filename):
    txt = open(Filename, 'r').read()
    return executeAndReturn_cursor(databaseName,txt)
      
        
def extract_NumberEnrollments(Name_database):
    txt='Select count(distinct user_id) from observed_events'
    c=executeAndReturn_cursor(Name_database,txt)[0][0]
    return c

### Resources

def extract_NumberResources(Name_database):
    txt='Select count(distinct resource_id) from resources'
    c=executeAndReturn_cursor(Name_database,txt)[0][0]
    txt="Select count(distinct resource_id) from resources where resource_type_id='0' "
    d=executeAndReturn_cursor(Name_database,txt)[0][0]
    txt="select count(*) from resources where resource_name=''"
    e=executeAndReturn_cursor(Name_database,txt)[0][0]
    txt="select count(*) from resources where resource_parent_id=''"
    f=executeAndReturn_cursor(Name_database,txt)[0][0]
    txt="select count(*) from resources where resource_child_number='0'"
    g=executeAndReturn_cursor(Name_database,txt)[0][0]
    return [c,d,e,f,g]

def extract_NumberProblems(Name_database):
    txt='Select count(*) from problems'
    c=executeAndReturn_cursor(Name_database,txt)[0][0]
    txt="Select count(*) from problems where problem_type_id='0' "
    d=executeAndReturn_cursor(Name_database,txt)[0][0]
    return [c,d]


### Observed Events
def extract_NumberObservedEvents(Name_database):
    txt='Select count(distinct observed_event_id) from observed_events'
    c=executeAndReturn_cursor(Name_database,txt)[0][0]
    return c  

def extract_NumberURL(Name_database):
    txt='Select count(*) from urls'
    c=executeAndReturn_cursor(Name_database,txt)[0][0]
    return c 

def extract_RangeTimeStamps(Name_database):
    txt="select observed_event_timestamp from observed_events order by observed_event_timestamp LIMIT 1"
    first=executeAndReturn_cursor(Name_database,txt)[0][0]
    txt="select observed_event_timestamp from observed_events order by -observed_event_timestamp LIMIT 1"
    last=executeAndReturn_cursor(Name_database,txt)[0][0]
    return [first,last]

def extract_NumberNegDur(Name_database):
    txt="select count(*) from observed_events where observed_event_duration<0"
    c=executeAndReturn_cursor(Name_database,txt)[0][0]
    return c


### COllaborations

def extract_NumberCollaboration(Name_database):
    txt='Select count(distinct collaboration_id) from collaborations'
    c=executeAndReturn_cursor(Name_database,txt)[0][0]
    return c

def extract_NumberSubmission(Name_database):
    txt='Select count(distinct submission_id) from submissions'
    c=executeAndReturn_cursor(Name_database,txt)[0][0]
    return c   


#### EXTRACTING GENERAL REPORT 
def extract_MainInfo(Name_database):
    file=open("Global report on "+Name_database+'.txt',"w")
    file.write("General report about course : "+Name_database+'\n')

    file.write('\n')
    file.write("Number of enrollments = "+str(extract_NumberEnrollments(Name_database))+'\n')

    file.write('\n')
    file.write('Resources :'+'\n')
    res=extract_NumberResources(Name_database)
    file.write("Number of resources = "+str(res[0])+'\n')
    file.write(" of which "+str(int(100*res[1]/res[0]))+"% do not have type"+'\n')
    file.write(" of which "+str(int(100*res[2]/res[0]))+"% do not have name"+'\n')
    file.write(" of which "+str(int(100*res[3]/res[0]))+"% do not have parent id"+'\n')
    file.write(" of which "+str(int(100*res[4]/res[0]))+"% do not have children resource"+'\n')
    pb=extract_NumberProblems(Name_database)
    file.write("Number of problems = "+str(pb[0])+" of which "+str(int(100*pb[1]/pb[0]))+"% do not have type"+'\n')

    file.write('\n')
    file.write('Observed Events :'+'\n')
    file.write("Number of observed events = "+str(extract_NumberObservedEvents(Name_database))+'\n')
    file.write(" of which "+str(extract_NumberNegDur(Name_database))+' have negative duration \n')
    file.write("Number of URLs = "+str(extract_NumberURL(Name_database))+'\n')
    ob=extract_RangeTimeStamps(Name_database)
    file.write("First observed event on :"+str(ob[0])+". Last observed event on :"+str(ob[1])+'\n')

    file.write('\n')
    file.write('Collaboration :'+'\n')
    file.write("Number of collaborations = "+str(extract_NumberCollaboration(Name_database))+'\n')

    file.write('\n')
    file.write('Submissions :'+'\n')
    file.write("Number of submissions = "+str(extract_NumberSubmission(Name_database))+'\n')
    file.close()
    
