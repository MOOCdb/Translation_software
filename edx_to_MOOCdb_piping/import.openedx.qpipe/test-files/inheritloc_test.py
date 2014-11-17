from helperclasses import *
from inheritloc import *

no_url_event ={'current_location':(CourseURL('http://a/b/'),'2013-11-10 06:43:41'),'time':'2013-12-10 06:44:00', 'page':'' }

no_url(no_url_event)

print no_url_event['page']

seq_level_event = {'current_location':(CourseURL('https://class.stanford.edu/courses/Medicine/SciWrite/Fall2013/courseware/c340d5c73f3a4e149bf2755adeef2e22/ff5b301018454eff862deb7a52553ca3/3/'),'2013-11-10 06:43:41'),'page':CourseURL('https://class.stanford.edu/courses/Medicine/SciWrite/Fall2013/courseware/c340d5c73f3a4e149bf2755adeef2e22/ff5b301018454eff862deb7a52553ca3/')}

inherit_seqnum(seq_level_event)

print str(seq_level_event['page'])

