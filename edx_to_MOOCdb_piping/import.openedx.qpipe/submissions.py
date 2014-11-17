from helperclasses import * 
from resources import ResourceHierarchy, Problem
import pickle
import os

class SubmissionManager(object):

    def __init__(self, moocdb):

        # Creates table writers
        self.problem_hierarchy = ResourceHierarchy(moocdb.problems, 'i4x://', Problem)
        self.submissions = moocdb.submissions
        self.assessments = moocdb.assessments
        
    
    def update_submission_tables(self,event):

        event_type = event['event_type']
        event_class = event.__class__.__name__
        
        # Only ProblemInteraction and OpenResponseAssessment
        # events are of interest here.
        if event_class not in ['ProblemInteraction','OpenResponseAssessment']:
            return
        
        # Insert problem into the hierarchy
        if event.data.get('module', None):
            problem_node = Problem(event.data['module'].get_uri())
            problem_node.resource_id = event['resource_id']
            event.set_data_attr('problem_id', self.problem_hierarchy.insert(problem_node))
        else:
            event.set_data_attr('problem_id','')

        # If the event is a submission, record the answer 
        # and update submissions table.
        if event.get_is_submitted() != -1:
            self.submissions.store(event.get_submission_row())

        # If the event is an assessment, udpdate assessments table
        if event.get_success() != None:
            self.assessments.store(event.get_assessment_row())

        
    def serialize(self, pretty_print_to=''):
        self.problem_hierarchy.serialize(pretty_print_to)
        
        
    

    

        

