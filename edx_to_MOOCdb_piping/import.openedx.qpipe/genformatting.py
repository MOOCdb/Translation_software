import httpagentparser
import helperclasses
import datetime
import re
import config as cfg

# Conveting IP address to an integer
def from_string(s):
    """Convert dotted IPv4 address to integer."""
    return reduce(lambda a,b: a<<8 | b, map(int, s.split(".")))

def ip_to_integer(raw_event):
    """Converts raw event 'ip' field to an integer"""
    dotted_ip = raw_event['ip']

    if '.' not in dotted_ip:
        return
 
    try:
        integer_ip = from_string(dotted_ip)
        raw_event['ip'] = integer_ip
    except Exception, e:
        print "Not a dotted IPv4 address: " + dotted_ip

# Parsing HTTP Agent header
def set_agent_os(raw_event):
    """ Parses the HTTP Agent header taken from the 'agent' field 
    of raw event, and sets 'agent' and 'os' fields."""
    os_and_agent = httpagentparser.simple_detect(raw_event['agent'])
    raw_event['os'] = os_and_agent[0]
    raw_event['agent'] = os_and_agent[1]

# Formatting the URL
def format_url(raw_event):
    """ Instanciates a CourseURL object from the 'page' field """
    raw_event['page'] = helperclasses.CourseURL(raw_event['page'])

# Parsing the timestamp
def parse_timestamp(raw_event):
    try:
        # Remove possible offset information
        # 2013-09-11T13:25:44.876729+00:00
        # 2013-09-11T13:25:44.876729
        timestamp = re.sub('\+.*$','',raw_event['time'])

        # Parse timestamp
        raw_event['time'] = datetime.datetime.strptime(timestamp,cfg.TIMESTAMP_FORMAT)

    except Exception as e:
        print '(!) Unable to parse timestamp for event #'+raw_event['_id']
        print e

# Parsing the problem_id field
def parse_problem_id(raw_event):
    '''Gives a consistent URI formatting to problem IDs.
    Example :
        i4x-MITx-6_002x-problem-H10P2_New_Impedances_10_1
      becomes:
        i4x://MITx/6.002x/problem/H10P2_New_Impedences/10/1/
    
    That way, URL hierarchy and problem hierarchy can be handled 
    similarly.
    '''
    
    if raw_event['answer_identifier']:
        problem_id = raw_event['answer_identifier']
    elif raw_event['problem_id']:
        problem_id = raw_event['problem_id']
    else:
       return

    raw_event['module'] = helperclasses.ModuleURI(problem_id)

# Parsing the video_id field
def parse_video_id(raw_event):
    '''
    Video ID can either be found in 'video_id' or 
    'transcript_id' fields.
    '''
    if raw_event['video_id']:
        video_id = raw_event['video_id']
    elif raw_event['transcript_id']:
        video_id = raw_event['transcript_id']
    else:
        return
    raw_event['module'] = helperclasses.ModuleURI(video_id)

def parse_question_location(raw_event):
    if raw_event['question_location']:
        raw_event['module'] = helperclasses.ModuleURI(raw_event['question_location'])
