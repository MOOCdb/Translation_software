# Usage :
# sh diagnosis.sh logFile

SCRIPT_DIR=`dirname $0`
 
# Sanity checks
LOG_FILE=$(readlink -f $1)

if [ ! -f "$LOG_FILE" ]
then
    echo "Wrong file or directory : $LOG_FILE"
    return
fi

# Change to the log file directory
LOG_DIR=$(dirname $LOG_FILE)
cd $LOG_DIR

# Go to info folder (create if necessary)
INFO="$LOG_DIR/info"

if [ ! -d "$INFO" ]
then
    echo "Creating /info directory..."
    mkdir info
fi

cd info

# Build the event taxonony 
echo "Building event typology..."
sh $SCRIPT_DIR/buildEventTypology.sh $LOG_FILE

# Build the i4x classification
echo "Classifying i4x events..."
sh $SCRIPT_DIR/classifyI4xEvents.sh $LOG_FILE

# Fetch the examples
EXAMPLES=$INFO"/examples"
if [ ! -d "$EXAMPLES" ]
then
    echo "Creating /examples directory"
    mkdir examples
fi

cd examples

echo "Fetching examples..."
sh $SCRIPT_DIR/fetchExamples.sh $LOG_FILE
sh $SCRIPT_DIR/fetchI4xExamples.sh $LOG_FILE

cd ..
echo "Cleaning up"
rm -v .all_event_types.txt
rm -v .path_styled_event_types.txt
rm -v .i4x_events.txt
