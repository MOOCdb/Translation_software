import re

# Formatting the problem_id field
PROBLEM_TAIL = re.compile('(?P<number>(_[0-9]{1,2})+)(?P<irrelevant>[^0-9]*)$')
PROBLEM_ROOT = 'i4x://MITx/6.002x/'

def format_problem_id(problem_id):
    '''Gives a consistent URI formatting to problem IDs.
    Example :
        i4x-MITx-6_002x-problem-H10P2_New_Impedances_10_1
      becomes:
        i4x://MITx/6.002x/problem/H10P2_New_Impedences/10/1/
    
    That way, URL hierarchy and problem hierarchy can be handled 
    similarly.
    '''
    global PROBLEM_TAIL, PROBLEM_HEAD
    
    # If the event has no problem_id, 
    # or if it already comes as a URI, 
    # we are done
    if not problem_id or 'i4x://' in problem_id:
        return problem_id

    # Keep only the specific part of the
    # problem ID, i.e. the one after 
    # '-problem-'
    parts = problem_id.split('-problem-')
    problem_id = parts[1]

    # Check if the problem ID has a tail,
    # i.e. numbers referring to a specific
    # question within the problem
    tail = PROBLEM_TAIL.search(problem_id)
    
    # If there is no tail, just add the i4x://
    # root to the identifier, and we are done
    if not tail:
        return PROBLEM_HEAD + problem_id

    # Remove irrelevant tail string, like 'dynamath' in:
    #   i4x-MITx-6_002x-problem-S24E1_Summing_Amplifier_2_1_dynamath
        
    l = len(tail.group('number')) + len(tail.group('irrelevant'))
    problem_id = problem_id[:-l]
    
    numbers = tail.group('number').replace('_','/')
    return PROBLEM_ROOT + problem_id + numbers


def format_video_id(raw_event):
    global PROBLEM_ROOT

    if raw_event['video_id']:
        video_id = raw_event['video_id']
    elif raw_event['transcript_id']:
        video_id = raw_event['transcript_id']
    else:
        return

    video_id = video_id.split('-video-')[1]
    
    raw_event['video_id'] = PROBLEM_ROOT + 'video/' + video_id




if __name__ == '__main__':

    pb1 = 'i4x-MITx-6_002x-problem-S21E2_LR_filter_2_1_dynamath'
    pb2 = 'i4x://MITx/6.002x/problem/S22E1_Which_output_'
    pb3 = 'i4x-MITx-6_002x-problem-Lab_0_Using_the_Tools_12_1'

    vid1 = {'video_id':'i4x-MITx-6_002x-video-S25V16_Op_Amp_oscillator'}
    
    v = [vid1]
    a = [pb1, pb2, pb3]

    for pb in v:
        format_video_id(pb)
        print pb['video_id']
