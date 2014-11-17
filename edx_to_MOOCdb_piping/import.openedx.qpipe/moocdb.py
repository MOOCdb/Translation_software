import os
import csv


class MOOCdb(object):
    """Provides an interface to store data into a MOOCdb instance. 
    The serialization may be MySQL or CSV"""

    #Important : primary key should be the first specified for each table
    TABLES = {'observed_events':['observed_event_id',
                                 'user_id',
                                 'url_id',
                                 'observed_event_timestamp',
                                 'observed_event_duration',
                                 'observed_event_ip',
                                 'observed_event_os',
                                 'observed_event_agent',
                                 'observed_event_type'],

              'resources':['resource_id',
                           'resource_name',
                           'resource_uri',
                           'resource_type_id',
                           'resource_parent_id',
                           'resource_child_number',
                           'resource_relevant_week',
                           'resource_release_timestamp'],
    
              'resources_urls':['resources_urls_id',
                                'resource_id',
                                'url_id'],

              'urls':['url_id',
                      'url'], 

              'resource_types':['resource_type_id',
                                'resource_type_content',
                                'resource_type_medium'],

              'problems':['problem_id',
                          'problem_name',
                          'problem_parent_id',
                          'problem_child_number',
                          'problem_type_id',
                          'problem_release_timestamp'
                          'problem_soft_deadline',
                          'problem_hard_deadline',
                          'problem_max_submission',
                          'problem_max_duration',
                          'problem_weight',
                          'resource_id'],

              'submissions':['submission_id',
                             'user_id',
                             'problem_id',
                             'submission_timestamp',
                             'submission_attempt_number',
                             'submission_answer',
                             'submission_is_submitted',
                             'submission_ip',
                             'submission_os',
                             'submission_agent'],

              'assessments':['assessment_id',
                             'submission_id',
                             'assessment_feedback',
                             'assessment_grade',
                             'assessment_grade_with_penalty',
                             'assessment_grader_id',
                             'assessment_timestamp'],

              'problem_types':['problem_type_id',
                               'problem_type_name'],
              'os':['os_id',
                    'os_name'],

              'agent':['agent_id',
                       'agent_name']  }

    def __init__(self,MOOCDB_DIR=''):
        self.create_csv_writers(MOOCDB_DIR)

    def close(self):
        for table in self.TABLES:
            reader = getattr(self,table)
            reader.close()

    def create_csv_writers(self,MOOCDB_DIR):
        for table in self.TABLES:
            setattr(self,table,CSVWriter(MOOCDB_DIR + table + '.csv', self.TABLES[table]))
        

class CSVWriter(object):
    
    def __init__(self,output_file,fields,delim=','):

        try:
            self.output = open(output_file,'w')
            self.writer = csv.DictWriter(self.output, delimiter=delim, fieldnames=fields, quotechar='"', escapechar='\\',lineterminator='\n')
        
        except IOError:
            #print '[' + self.__class__.__name__ + '] Could not open file ' + output_file
            return

    def store(self,l):
        self.writer.writerow(l)
        
    def close(self):
        self.output.close()
        


