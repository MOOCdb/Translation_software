import re
import helperclasses
import config as cfg

# Handles formatting of raw i4x events
def format_i4x(raw_event):
    # Parsing event_type 
    module = helperclasses.ModuleURI(raw_event['event_type'])

    # Construct and set event_type
    raw_event['event_type'] = 'i4x_' + str(module.category) + '_' + str(module.action)
    
    # Set module if missing
    if 'module' not in raw_event:
        raw_event['module'] = module


def format_url_change(raw_event):

    URL_ROOT = cfg.DOMAIN
    
    # Instanciate CourseURL object
    url_string = URL_ROOT + raw_event['event_type']
    url = helperclasses.CourseURL(url_string)
    
    # If the URL is a sub-unit level,
    # append /1 since user will land on first sequence.
    if url.get_sub_unit() and not url.get_seq():
        url.set_seq('1')

    # Set url
    raw_event['page'] = url        

    # Set event type
    raw_event['event_type'] = 'url_change'
    

def format_seq(raw_event):
    '''
    In order to compute duration correctly,
    a sequence switching event must be interpreted
    as happening on goto_dest.
    '''

    url = raw_event['page']
    goto_dest = raw_event['goto_dest']
    
    if not goto_dest:
        #print 'Missing goto_dest in seq event %s'%event['_id']
        return

    if url.get_sub_unit():
        url.set_seq(goto_dest)

def format_book(raw_event):
    '''
    Adds the book interation type to event_type
    Set the page number in the URL to 
    goto_dest.
    '''
    raw_event['event_type'] += '_' + raw_event['book_interaction_type']
    raw_event['page'].set_page(raw_event['goto_dest'])
