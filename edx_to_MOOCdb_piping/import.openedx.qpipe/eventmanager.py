from helperclasses import *

class EventManager():
        
    IGNORE = ['page_close',
              'problem_check',
              'problem_check_fail',
              'problem_graded',
              'save_problem_check',
              'i4x_problem_problem_check',
              'save_problem_success',
              'problem_save',
              'i4x_problem_problem_save',
              'save_problem_check_fail',
              'reset_problem',
              'reset_problem_fail',
              'problem_reset',
              'save_problem_fail']

    def __init__(self, moocdb=None):
        self.STAGED_EVENTS = {}
        if moocdb:
            self.observed_events = moocdb.observed_events

    def stage_event(self,event):
        user = event['anon_screen_name']
        
        # Page close gives no information on the user's location
        # *after* the event occured. Therefore, it is ignored.

        if event.data.get('event_type',None) in self.IGNORE:
            return None

        if user in self.STAGED_EVENTS.keys():
            ending_event = self.STAGED_EVENTS[user]
            end_time = event.data['time']
            
            # Compute event duration
            ending_event.set_duration(end_time)

            # Stage new event
            self.STAGED_EVENTS[user] = event

            # Return ending event, ready for insertion
            return ending_event
        else:
            self.STAGED_EVENTS[user] = event
            return None

    def store_event(self, event):
  
        event_to_store = self.stage_event(event)

        if event_to_store:
            self.observed_events.store(event_to_store.get_observed_event_row())
        
    def serialize(self):

        for e in self.STAGED_EVENTS.values():
            self.observed_events.store(e.get_observed_event_row())
            

