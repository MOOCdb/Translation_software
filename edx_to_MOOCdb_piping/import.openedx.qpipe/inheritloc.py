# These functions suppose that the user is engaged
# and that the location is not obsolete

# If the event has no URL, just inherit current location
def no_url(raw_event):
    '''
    URL inheritance:
    If the URL is missing, inherit the user's current location
    '''

    # Interaction events should only inherit URLs that are at subunit level
    current_location = raw_event['current_location'][0]

    if current_location.get_sub_unit():
        raw_event['page'] = current_location
        raw_event['inherited'] = 'url'
        print '[inheritloc.no_url] Inherited location : ' + str( current_location )

    else:
        raw_event['inherited'] = ''
        print '[inheritloc.no_url] Location was not inherited because not at sub-unit level.'
    

def inherit_seqnum(raw_event):
    """ 
    Granularity inheritance
    Assumes that raw_event page is at sub-unit level,
    and tries to inherit the sequence number of the user's current location
    """

    current_location = raw_event['current_location'][0]
    event_url = raw_event['page']
    
    same_unit = current_location.get_unit() == event_url.get_unit()
    same_sub_unit = current_location.get_sub_unit() == event_url.get_sub_unit()

    if same_unit and same_sub_unit:

        seqnum = current_location.get_seq()
        
        if seqnum:

            event_url.set_seq(seqnum)
            raw_event['inherited'] = 'seqnum'
            
        else:

            print '[inheritloc.inherit_seqnum] Previous location ( ' + str(current_location) + ' ) has no seqnum.'

    else:

        print '[inheritloc.inherit_seqnum] No inheritance : units did not coincide.'



    
