#import MySQLdb
import csv
import os
import pickle
import pandas as pd
import config as cfg

def get_events():
    src = cfg.INPUT_SOURCE
    if src=='csv':
        return CSVExtractor()
    elif src=='mysql':
        return MySQLExtractor()
    elif src=='json':
        return JSONExtractor()

class CSVExtractor(object):
    """ 
    Loads data from CSV export of Stanford datastage tables
    """
    
    # CSV Fields 
    ANSWER_FIELDNAMES = ['answer_id','problem_id','answer','course_id']
    CORRECT_MAP_FIELDNAMES = ['correct_map_id','answer_identifier', 'correctness','npoints','msg','hint','hintmode','queustate']
    EDX_TRACK_EVENT_FIELDNAMES = ['_id','event_id','agent','event_source','event_type','ip','page','session','time','anon_screen_name','downtime_for','student_id','instructor_id','course_id','course_display_name','resource_display_name','organization','sequence_id','goto_from','goto_dest','problem_id','problem_choice','question_location','submission_id','attempts','long_answer','student_file','can_upload_file','feedback','feedback_response_selected','transcript_id','transcript_code','rubric_selection','rubric_category','video_id','video_code','video_current_time','video_speed','video_old_time','video_new_time','video_seek_type','video_new_speed','video_old_speed','book_interaction_type','success','answer_id','hint','hintmode','msg','npoints','queuestate','orig_score','new_score','orig_total','new_total','event_name','group_user','group_action','position','badly_formatted','correctMap_fk','answer_fk','state_fk','load_info_fk']

    def __init__(self, edx_track_event=cfg.EDX_TRACK_EVENT, answer=cfg.ANSWER, correct_map=cfg.CORRECT_MAP):
        # Create a CSV reader for the EdxTrackEvent table
        try:
            events = open(edx_track_event)
            self.edx_track_event = csv.DictReader( events,
                                                   fieldnames=self.EDX_TRACK_EVENT_FIELDNAMES,
                                                   delimiter=',',
                                                   quotechar=cfg.QUOTECHAR,
                                                   escapechar='\\')
        except IOError as e:
            print 'Unable to open EdxTrackEvent file : %s'% cfg.EDX_TRACK_EVENT
            exit

        # Load Answer and CorrectMap tables into pandas DataFrames,
        # indexed by the table's primary key.
        try:
            self.answer = pd.read_csv(answer, delimiter=',', quotechar=cfg.QUOTECHAR, index_col=0, names=self.ANSWER_FIELDNAMES, dtype='string')
            self.correct_map = pd.read_csv(correct_map, delimiter=',', quotechar=cfg.QUOTECHAR, index_col=0, names=self.CORRECT_MAP_FIELDNAMES,dtype='string')
        except Exception as e:
            print 'Pandas unable to load CSV :'
            print str(e)
            exit
    
    def __iter__(self):
        return self

    def next(self):
        event = self.edx_track_event.next()
        print '* Making joins'
        self.get_foreign_values(event, 'answer_fk', ['answer'], self.answer)
        self.get_foreign_values(event, 'correctMap_fk', ['answer_identifier', 'correctness'], self.correct_map)
        return event
    
    def new_reader(self, input_file, field_names, delim=',', qtchar='\'', escchar='\\'):
        try:
              return 
        except IOError:
            print '[CSVExtractor.new_reader] Could not open file : ' + input_file
            return

    def get_foreign_values(self, event, fkey_name, fval_names, dataframe):
        '''
        This method adds to the EdxTrackEvent row the relevant
        fields fetched from a foreign table.
        It performs the analog of a SQL join with fk_dict on foreign_key_name.

        In case of conflict (foreign field holding same information and having
        same name as local field), the local value is kept if non empty and
        overridden otherwise. 
        
        foreign_key: value of the foreign key on which the join is performed
        fk_dict: dictionary mapping foreign keys to foreign values
        '''

        fkey = event.get(fkey_name, None)
        
        if fkey:           
            try:
                frow = dataframe.loc[fkey]
                for name in fval_names:
                    event[name] = frow.loc[name]
            except Exception as e:
                print 'Broken foreign key : %s'%fkey
                print str(e)
                exit
        
        # If the foreign key is missing, set all foreign 
        # fields to ''
        else:
            for name in fval_names:
                event[name]=''
            
        

        
        

