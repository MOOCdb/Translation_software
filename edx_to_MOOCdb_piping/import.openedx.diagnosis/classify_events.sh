#!/bin/bash


# Record the date of the diagnosis,
# the size of the log file
# and the total number of events.
function get_general_info {
    date ; 
    du -h $LOG_FILE ;
    wc -l $LOG_FILE ; } > $STATS


# Extract and sort all (<event_type>, <event_source>) pairs from logfile.
# Repetitions are kept at sorting to allow for future
# use of 'uniq -c', that performs the aggregate counts
# Usage : 
# get_all_event_types <log_file> <output_file>

function get_all_event_types {
sed 's#^.*"event_source"[^:]*:[ ]*"\([^"]*\)".*"event_type"[^:]*:[ ]*"\([^"]*\)".*$#\2 \1#g' $1 \
    | sort > $2 ; } 


# Separates regular event types from module interaction 
# and page access events. One file is created for each.
#
# Usage :
# dispatch_events <all_events> <regular> <module> <page_access>

function dispatch_events {

    echo "Dispatching events..."

    # Empty output files
    cat /dev/null > $2
    cat /dev/null > $3
    cat /dev/null > $4

    while read type source
    do
	case "$type" in
	    # $line is a module interaction event
	    *i4x:*) echo "$type" >> $3  ;;
            # $line is a page access event
	    /*) echo "$type" >> $4 ;;
	    # $line is a regular event
	    *) echo "$type $source" >> $2 ;;
	esac
    done < $1 ; }


# Extract category and action of each module interaction event.
# Usage:
# classify_module <module events>

function classify_module {

    echo "Classifying module interaction events..." ;

    sed -r 's#^.*i4x://?[^/]*/[^/]*/([^/]*)/[^/]*/?([^ ]*).*$#\1 \2#g' $1 > /tmp/i4xcateg ;
    cat /tmp/i4xcateg > $1 ;
    rm /tmp/i4xcateg ; } 


# Sort the regular event types
function sort_events {

    echo "Sorting $1..." ;

    cat $1 | sort | uniq -c | sort -n -r > /tmp/sort ;
    cat /tmp/sort > $1 ;
    rm /tmp/sort ; }

# Main function gluing the pieces together
# to build the event classification and fetch

function classify_events {
    
    echo "Building event classification..."
    
    # Create diagnosis directory 
    DIAG_DIR='diagnosis'
    mkdir -p $DIAG_DIR
    
    # Input file is read from the command line
    # TODO Sanity checkings
    LOG_FILE=$1

    # Output files
    STATS=$DIAG_DIR'/info'
    ALL=$DIAG_DIR'/.all'
    REGULAR=$DIAG_DIR'/regular'
    MODULE=$DIAG_DIR'/module'
    ACCESS=$DIAG_DIR'/access'

    get_general_info $1 ;

    # Getting all the event types
    get_all_event_types $1 $ALL ;

    # Separating events 
    dispatch_events $ALL $REGULAR $MODULE $ACCESS ;

    # Classifying module events
    classify_module $MODULE ;

    # Sorting with multiplicity
    sort_events $REGULAR ;
    sort_events $MODULE ;
    sort_events $ACCESS ; }

