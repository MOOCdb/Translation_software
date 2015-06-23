'''
Created on 15 January 2015

@author: Sebastien Boyer

Curates the resource table by infering the resource type using the uri's.
'''
import MySQLdb
import numpy as np
from sql_functions import *



def extract_NumberEnrollments(conn):
    txt='Select count(distinct user_id) from observed_events'
    cursor = conn.cursor()
    cursor.execute(txt)
    c = cursor.fetchone()
    cursor.close()
    if c:
        c = c[0][0]
    return c


######################################### POPUlATING RESOURCE IDs

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
def populate_resource_type(dbName, userName, passwd, host, port):

    conn = openSQLConnectionP(dbName, userName, passwd, host, port)
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



