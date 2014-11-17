import copy

# Each rule has to return the new location of the user
# If the user is previously engaged, the 'current_location' field is available in raw_event
# So engagement should be checked with "'current_location' in raw_event.keys()"

def simple_update(raw_event):
    return raw_event['page']

def update_seq(raw_event):
    
    url_copy = copy.copy(raw_event['page'])
    url_copy.set_seq(raw_event['goto_dest'])
    return url_copy

def close_previous_page(raw_event):

    # If the user's previous location is not known,
    # page_close doesn't give further information,
    # so return None

    if 'current_location' not in raw_event.keys():
        return None

    current_location = raw_event['current_location'][0]
    closed_url = raw_event['page']
    
    s = closed_url.get_unit() 
    if closed_url.get_sub_unit():
        s+= closed_url.get_sub_unit()

    if s in str(current_location):
        return None
    else:
        #print 'Page not closed : ' + str(current_location)
        #print '\t page_close unit : ' + s
        return current_location

    
