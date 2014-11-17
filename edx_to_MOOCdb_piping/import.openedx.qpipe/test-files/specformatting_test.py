from specformatting import *
from helperclasses import *

i4x = {'event_type':'/courses/Medicine/SciWrite/Fall2013/modx/i4x://Medicine/SciWrite/sequential/ff5b301018454eff862deb7a52553ca3/goto_position'}

url_change_seq = {'event_type':'/courses/Medicine/SciWrite/Fall2013/courseware/c340d5c73f3a4e149bf2755adeef2e22/71f11e7c2f18459bbcc3f6ad1f0d6c78/1/'}
url_change_no_seq = {'event_type':'/courses/Medicine/SciWrite/Fall2013/courseware/c340d5c73f3a4e149bf2755adeef2e22/71f11e7c2f18459bbcc3f6ad1f0d6c78/'}
url_change_unit = {'event_type':'/courses/Medicine/SciWrite/Fall2013/courseware/c340d5c73f3a4e149bf2755adeef2e22/'}

seq = {'page':CourseURL('https://class.stanford.edu/courses/Medicine/SciWrite/Fall2013/courseware/c340d5c73f3a4e149bf2755adeef2e22/ff5b301018454eff862deb7a52553ca3/'),
       'goto_from':'2'}

format_i4x(i4x)
print i4x
format_seq(seq)
print seq
format_url_change(url_change_no_seq)
print url_change_no_seq['page']
