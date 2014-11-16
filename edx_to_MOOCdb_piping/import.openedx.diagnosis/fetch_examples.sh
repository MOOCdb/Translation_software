#!/bin/bash

# Script that fetches examples for each 
# event type found by doctorEdx.sh
# Should be executed in info/examples

LOG_FILE=$1
REGULAR='regular'
MODULE='module'
ACCESS='access'

HOW_MANY=100

# Removes IP and username from JSON lines
function anonymize {
    sed 's#"username"[ ]*:[ ]*"[^"]*"#"username":"A.N. ONyme"#g' $1 \
	| sed 's#"ip"[ ]*:[ ]*"[^"]*"#"ip":"nnn.nnn.nnn"#g' ; }

# Fetching examples of regular events
# Usage:
# fetch_regular_examples <logfile> <event types>

function fetch_regular_examples {
    
    mkdir -p examples 

    # Each line in $EVENT_TYPE should corresponds to one event type
    while read number event_type event_source
    do
	if [ -z "$event_type" ]
	then
	    continue
	fi

	if [ -z "$event_source" ]
	then
	    echo "Missing event_source for event type "$event_type
	    continue
	fi

	output_file='examples/'$event_type"_"$event_source".json"

	echo "Fetching examples for ( $event_source ,  $event_type )"

	regexp='"'$event_source'".*"'$event_type'"'

	grep -m $HOW_MANY $regexp $1 | anonymize > $output_file
    
    done < $2 ; }

# Usage:
# fetch_module_examples <logfile> <event types>

function fetch_module_examples {

    # Create examples subdirectory if it does not exist
    mkdir -p examples

    while read number category action
    do
    # Each non blank line should at least
    # have a category specified
	if [ -z "$category" ]
	then
	    continue
	fi

	output_file="examples/module_""$category"
	regexp='i4x:/[^"]*'$category

	if [ -n "$action" ]
	then
	    output_file="$output_file""_$action"
	    regexp="$regexp"'[^"]*'"$action"
	fi

	echo "Fetching examples of $category $action ..."
	grep -m $HOW_MANY $regexp $1 | anonymize > $output_file".json"  
    
    done < $2 ; }

# Fetches page access event examples for the
# most frequently accessed URL

function fetch_access_examples {
    
    mkdir -p examples

    echo "Fetching page access event examples..." ;
    read number path < $2 ;
    grep -m $HOW_MANY '"event_type"[ ]*:[ ]*"'"$path"'"' $1 | anonymize > 'examples/access.json' ; }

# Main function gluing all the pieces together 
# and fetching an anonymized sample of examples 
# representative of the data. 
# Usage:
# fetch_examples <logfile> 
# (Assumes that event classification is built) 

function fetch_examples {
    echo "Fetching examples..."
    fetch_regular_examples $1 'regular'
    fetch_module_examples $1 'module'
    fetch_access_examples $1 'access'
}
