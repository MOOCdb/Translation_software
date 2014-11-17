class Event(object):
    '''
    Class generating taking care of the common event
    properties...
    '''
    def __init__(self,polished_event):
        self.data = polished_event
        self.duration = 0

    def get_observed_event_row(self):
        '''
        Returns an array corresponding to a line in MOOCdb.observed_events.

        'event_type' and 'resource_id' fields are added, though not mentionned yet
        in MOOCdb specifications. 

        Note that observed_event_id is *not* a unique identifier, since
        a user interaction  may yield several rows in the intermediary DB.
        '''
        
        return { 'observed_event_id':self['_id'],
                 'user_id':self['anon_screen_name'],
                 'url_id':self['resource_id'],
                 'observed_event_timestamp':self['time'],
                 'observed_event_duration':self.duration,
                 'observed_event_ip':self['ip'],
                 'observed_event_os':self['os'],
                 'observed_event_agent':self['agent'],
                 # Additional fields, not in MOOCdb documentation (yet)
                 'observed_event_type':self['event_type']
        }

    def __getitem__(self, key):
        item = self.data.get(key)
        return str(item)

    def set_data_attr(self, key, value):
            
        if not value:
            return

        self.data[key] = value

    def get_uri(self):
        url = self['page'] if self['page'] else 'https://unknown/' 
        module = self.data.get('module','')
        if module:
            return url + module.get_relative_uri()
        else:
            return url

    def get_resource_display_name(self):
        name = self.data.get('resource_display_name','')
        if not name:
            module = self.data.get('module')
            if module:
                name = module.get_name()
        return name


    def set_duration(self,end_time):
        '''
        Computes the duration of an event in minutes, by taking the difference
        between the event's timestamp and a given end time.
        '''
        self.duration = (end_time - self.data['time']).seconds/60
        
    

class VideoInteraction(Event):
    '''
    Corresponds to the 'Video Interaction Event' type in [edXdocs]
    VideoInteraction class is instanciated from the following raw_events :
    
    play_video                        
    pause_video                       
    seek_video                        
    load_video                        
    speed_change_video       
    fullscreen 
    not_fullscreen 
    hide_transcript
    show_transcript
    '''
    def __init__(self,polished_event):
        super(VideoInteraction,self).__init__(polished_event)

    def get_video_code(self):
        if self['video_code']:
            return self['video_code']
        else:
            return self['transcript_code']
            
    def get_uri(self):
        uri = super(VideoInteraction,self).get_uri()
        video_code = self.get_video_code()
        return uri + '_' + video_code

class PdfInteraction(Event): 
    """
    Corresponds to the 'PDF Interaction Event Types' in [readthedocs]
    Instanciated from the following raw event types:
      - book 
    """

    def __init__(self, polished_event):
        super(PdfInteraction,self).__init__(polished_event)
        self.set_page(self['goto_dest'])

    def set_page(self, page):
        url = self.data['page']
        url.set_seq(page)

    
class ProblemInteraction(Event):
    '''
    Corresponds to the 'Problem Interaction Event Types' in [edXdocs].
    This event class is used to generate the rows of the Submission mode 
    tables in MOOCdb (submissions, assessments, problems)

    ProblemInteraction events are instanciated from raw events catched by 
    the corresponding rule in instancition_rls.txt. 

    These are :

    - problem_check (Server)
      '[edXdocs] The server fires problem_check events when a problem is successfully checked'
    - problem_check (Browser)
      '[edXdocs] A browser fires problem_check events when a user wants to check a problem.'
    - problem_check_fail (Server)
      '[edXdocs] The server fires problem_check_fail events when a problem cannot be checked successfully.'
    - problem_reset (Browser)
      '[edXdocs] Events fire when a user resets a problem
    - reset_problem (Server)
      '[edXdocs] Fires when a problem has been reset successfully' 
    - problem_save (Browser)
    - problem_show (Browser)                     
    - showanswer (Server)
      '[edXdocs] Server-side event which displays the answer to a problem'
    - save_problem_fail ( Server )
    - save_problem_success ( Server )                 
    - problem_graded                    
    - i4x_problem_input_ajax
    - i4x_problem_problem_check
    - i4x_problem_problem_get
    - i4x_problem_problem_reset
    - i4x_problem_problem_save
    - i4x_problem_problem_show
    

    [edXdocs] : edx.readthedocs.org/projects/devdata/en/latest/internal_data_formats/tracking_logs.html
    '''

    
    # Different codes for the submission status
    # 1 : Answer is submitted
    # 0 : Answer is saved
    # 2 : Failure 
    # 3 : Reset

    IS_SUBMITTED = {'problem_check':1,
                    'problem_check_fail':2,
                    'problem_graded':1,
                    'i4x_problem_problem_check':1,
                    'save_problem_check':1,
                    'save_problem_success':0,
                    'problem_save':0,
                    'i4x_problem_problem_save':0,
                    'save_problem_check_fail':2,
                    'reset_problem':3,
                    'reset_problem_fail':2,
                    'problem_reset':3,
                    'save_problem_fail':2}

    # Events that are use to populate assessment table
    # (These are all associated to automatic assessments)
    ASSESSMENT_EVENTS = {'save_problem_check',
                         'problem_check' }

    GRADE_DICT = { 'correct':1, 'incorrect':0 }

    def __init__(self,raw_event):
        super(ProblemInteraction,self).__init__(raw_event)
        

    def get_answer(self):
        '''
        -- Added while processing SolarFall2013 ---

        Accomodates the following scenario :
          problem_id : input_i4x-Engineering-Solar-problem-bc31c9ab2dab4bba8ad8f716f8ecf8d5_2_1_choice_2
          answer : correct
          correctness : <missing>
        
        Here, the student answer is choice_2, which is embedded in the problem ID.
        This answer is rescued by ModuleURI when parsing the problem_id string.

        The given answer value is in fact the correctness of 'choice_2'. Accordingly,
        with help of the ModuleURI object, this method rearranges things as :
          problem_id : i4x://Engineering/Solar/problem/bc31c9ab2dab4bba8ad8f716f8ecf8d5/2/1
          answer : choice_2
          correctness : correct

        '''
        try:
            if self.data.get('module').rescued_answer:
                if not self['answer']:
                    self.set_data_attr('answer', rescued_answer) 
                if self['answer'] in ['correct','incorrect']:
                    self.set_data_attr('success', self['answer'])
                    self.set_data_attr('answer', rescued_answer)
                    #print 'Rescued answer !'
        except Exception as e:
            print 'Exception while rescuing answer : %s'%str(e)
        finally:
            return self['answer']
                    
    def get_success(self):
        '''
        Server problem_check events come with a 'success' field indicating
        wether the answer checked is correct.
        If the 'success' field is absent, we can fallback on CorrectMap.correctness
        '''

        correctness = self.data.get('correctness',None)
        if not correctness:
            return

        try:
            return self.GRADE_DICT[correctness]
        except KeyError as e:
            print e
            print 'Unknown correctness value :%s'%correctness
                
    def get_is_submitted(self):
        ''' 
        Deduce from the event_type wether an answer is being
        submitted or just saved.
        '''
        return self.IS_SUBMITTED.get(self['event_type'],-1)
                                      

    def get_submission_row(self):
        '''
        Returns an array corresponding to a row in MOOCdb.submissions        
        Note that 'submission_id' is absent : it will be generated by 
        the SubmissionManager instance. 
        '''
        return { 'submission_id':self['_id'],
                 'user_id':self['anon_screen_name'],
                 'problem_id':self['problem_id'],
                 'submission_timestamp':self['time'],
                 'submission_attempt_number':self['attempts'],
                 'submission_ip':self['ip'],
                 'submission_os':self['os'],
                 'submission_agent':self['agent'],
                 'submission_answer':self['answer'],
                 'submission_is_submitted':self.get_is_submitted() 
        }
        
    def get_assessment_row(self):
        '''
        Returns an array corresponding to a row in MOOCdb.assessments.
        'assessment_id' (primary key) and 'submission_id' (foreign key) 
        will be generated by SubmissionManager instance.

        Since each event records an answer to a specific question, 
        the grade is binary : either 'correct' or 'incorrect'
        '''
        return { 'assessment_grader_id':'automatic',
                 'assessment_timestamp':self['time'],
                 'assessment_grade':self.get_success(),
                 'submission_id':self['_id'],
                 'assessment_id':self['_id'] 
        }

    

class OpenResponseAssessment(Event):
    ''' 
    Corresponds to the 'Open Response Assessment Event Types' in [edXdocs]
    Instanciated from the following raw event types : 

    - oe_hide_question (Browser)                 
    - oe_show_question (Browser)           
      '[readthedocs] Fires when the user hides or redisplays a combined open-ended problem.'

    - rubric_select (Browser)

    - i4x_combinedopenended_<action> (Server)

    - peer_grading_<action> (Browser)       
    - staff_grading_<action> (Browser)
    - i4x_peergrading_<action> (Server)
    '''

    def __init__(self,raw_event):
        super(OpenResponseAssessment,self).__init__(raw_event)
    

    def get_problem_row(self):
        '''
        Returns an array corresponding to a row in MOOCdb.problem
        
        'problem_id' *should* be at question granularity

        Many fields are missing, because a large part of the data
        is not captured in the tracking logs. These will be crowdsourced.

        '''
        
        return { 'problem_id':self['module'],
                 'problem_name':self.get_resource_display_name(),
                 'resource_id':self['resource_id ']
        }

    # No support yet for open response submissions
    def get_is_submitted(self):
        return -1

    def get_success(self):
        return None

class Navigational(Event):
    """
    Corresponds to the 'Navigational Event Types' in [readthedocs]
    Instanciated from events :
    - seq_goto
    - seq_prev
    - seq_next
    """

    def __init__(self, raw_event):
        super(Navigational,self).__init__(raw_event)
        self.sequence_id = raw_event['sequence_id']
        self.goto_dest = raw_event['goto_dest']
        self.goto_from = raw_event['goto_from']

    def get_uri(self):
        # For navigational events,
        # module relative path should not be appended
        return self['page']
