#!/bin/bash

# Loops through MOOCdb csv folders and computes for each 
# a set of counts.
# Writes output to a csv file.
CSV_DIR=/data/csv/moocdb_csv
OUT=$CSV_DIR"/stats.csv"

cd $CSV_DIR
echo "Course, Enrollments, Resources, Observed events, Collaborations, Submissions" > $OUT

for folder in */
do
    cd $folder

    course="$folder"
    enrollments=`cut -d, -f2 observed_events.csv | sort -u | wc -l | awk {'print $1'}`
    num_resources=`wc -l resources.csv | awk {'print $1'}`
    num_observed_events=`wc -l observed_events.csv | awk {'print $1'}`
    num_submissions=`wc -l submissions.csv | awk {'print $1'}`

    cd $CSV_DIR
    echo $course", "$enrollments", "$num_resources", "$num_observed_events", 0, "$num_submissions >> $OUT
done
    

    
    
    
