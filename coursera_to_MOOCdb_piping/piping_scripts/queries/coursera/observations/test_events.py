from ....utilities import db, moocdb_utils
from datetime import datetime
import phpserialize
import json

def GetTestEvents(vars, original_item_id):
    # DB connections
    # --------------
    s = vars['source']
    general_db_selector = db.Selector(s['host'], s['user'], s['password'], s['port'], s['general_db'])
    
    oe_type_map = moocdb_utils.GetObservedEventTypeMap(vars)
    events = []
    
    if 'quiz_' in original_item_id:
        
        # Get submission metadata
        q = "SELECT * FROM quiz_submission_metadata JOIN `{0}`.hash_mapping USING ({1}) WHERE item_id={2}".format(vars['source']['hash_mapping_db'], vars['general_anon_col_name'], original_item_id.replace('quiz_', ''))
        if vars['options']['debug']:
            q += " AND {} IN ({})".format(vars['general_anon_col_name'], ",".join(vars['hash_map']['qls_general']))
        rows = general_db_selector.query(q)
        submission_metadata = {row['id']: {'user_original_id': vars['hash_map']['map_general'][row[vars['general_anon_col_name']]]} for row in rows}
        
        if len(submission_metadata) > 0:
            # Get submission content from kvs table
            in_list = ["'submission.submission_id:{}'".format(submission['id']) for submission in rows]
            in_list_string = ",".join(in_list)
            
            table_name = "kvs_course.{}.quiz".format(vars['source']['course_id']) if vars['source']['platform_format'] == 'coursera_1' else "kvs_course.quiz"
            q = "SELECT * FROM `{}` WHERE `key` IN ({})".format(table_name, in_list_string)
            rows = general_db_selector.query(q)
            user_event_params = {}
            for row in rows:
                try:
                    value = phpserialize.loads(phpserialize.loads(row['value']))
                except:
                    vars['logger'].Log(vars, "\t\t\tFailed to deserialize php-serialized string: {}\n\t\t\tSkipping this record".format(row['value']))
                    continue
                    
                key_parts = row['key'].split(":")
                submission_id = int(key_parts[1])
                uoid = submission_metadata[submission_id]['user_original_id']                    
                if uoid not in user_event_params.keys(): user_event_params[uoid] = []
                user_event_params[uoid].append({'event_type': 'started', 'timestamp': value['start_time']})
                user_event_params[uoid].append({'event_type': 'submitted', 'timestamp': value['saved_time']})
                
            for uoid in user_event_params.keys():
                submits = [x for x in user_event_params[uoid] if x['event_type'] == 'submitted']
                filtered_starts = []
                for x in user_event_params[uoid]:
                    if x['event_type'] == 'started':
                        retain_start = True
                        for y in submits:
                            if y['timestamp'] < x['timestamp'] and y['timestamp'] > (x['timestamp'] - 120):
                                retain_start = False
                                break
                        if retain_start:
                            filtered_starts.append(x)
                            
                for x in filtered_starts:
                    events.append({
                        'user_original_id': uoid,
                        'item_type': 'tests',
                        'item_original_id': original_item_id,
                        'observed_event_type_id': oe_type_map['test_visit'],
                        'observed_event_timestamp': datetime.fromtimestamp(x['timestamp']),
                        'observed_event_data': json.dumps({}),
                    })
                    
                for x in submits:
                    events.append({
                        'user_original_id': uoid,
                        'item_type': 'tests',
                        'item_original_id': original_item_id,
                        'observed_event_type_id': oe_type_map['test_submission'],
                        'observed_event_timestamp': datetime.fromtimestamp(x['timestamp']),
                        'observed_event_data': json.dumps({}),
                    })
                    
    return events