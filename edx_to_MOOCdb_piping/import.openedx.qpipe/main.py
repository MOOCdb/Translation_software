# Author : Quentin Agren <quentin.agren@gmail.com>

import sys
import os 
import extractor
import config as cfg

from events import *
from resources import *
from eventformatter import *
from eventmanager import *
from helperclasses import *
from submissions import *
from util import * 
from moocdb import MOOCdb

ROOT_DIR = os.getcwd()
MOOCDB_DIR = cfg.DEST_DIR
CONFIG_DIR = ROOT_DIR + '/config/'

# Log file, best viewed with emacs org-mode
LOG = cfg.LOG_FILE
sys.stdout = open(LOG, 'w+')

# File to pretty print resource hierarchy
HIERARCHY = cfg.RESOURCE_HIERARCHY
PB_HIERARCHY = cfg.PROBLEM_HIERARCHY

# MOOCdb storage interface
# TODO Apply branching to allow different options
moocdb = MOOCdb(MOOCDB_DIR)

# Instanciating the piping architecture
event_formatter = EventFormatter(moocdb, CONFIG_DIR)
resource_manager = ResourceManager(moocdb, HIERARCHY_ROOT='https://', CONFIG_PATH = CONFIG_DIR)
event_manager = EventManager(moocdb)
submission_manager = SubmissionManager(moocdb)
curation_helper = CurationHelper(MOOCDB_DIR)

print '**Processing events**' 

for raw_event in extractor.get_events():
        
    print '* Processing event #' + raw_event['event_id'] + ' @ ' + raw_event['page']
    print '** Applying filter'

    # Apply event filter
    if event_formatter.pass_filter(raw_event) == False:
        print 'Event filtered out'
        continue
            
    # Format raw event and instanciate corresponding Event subclass
    event = event_formatter.polish(raw_event)
    # print '- Instanciated event :: ' + event['event_type'] + '->' + event.__class__.__name__
    
    # Inserts resource into the hierarchy
    print '** Inserting resource'
    resource_id = resource_manager.create_resource(event)
    event.set_data_attr('resource_id', resource_id)

    # Store submission, assessment and problem
    submission_manager.update_submission_tables(event)

    # Record curation hints
    curation_helper.record_curation_hints(event)

    # Store observed event
    event_manager.store_event(event)

print '* All events processed'
print '** Writing CSV output to : ' + MOOCDB_DIR

event_formatter.serialize()
event_manager.serialize()
resource_manager.serialize(pretty_print_to=HIERARCHY)
submission_manager.serialize(pretty_print_to=PB_HIERARCHY)
curation_helper.serialize()

print '* Writing resource hierarchy to : ' + HIERARCHY
print '* Writing problem hierarchy to : ' + PB_HIERARCHY
# Close all opened files
moocdb.close()
