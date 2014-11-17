from updateloc import *
from helperclasses import *

# Page close when current location is not equal to page closed
e1 = {'page':CourseURL('https://class.stanford.edu/courses/Medicine/SciWrite/Fall2013/courseware/875108aedf9549808fef9b1453c5a4ee/'),
      'event_type':'page_close',
      'current_location':(CourseURL('https://class.stanford.edu/courses/Medicine/SciWrite/Fall2013/courseware/875108aedf9549808fef9b1564c5a4ee/'),'')}

# Page close when current location is equal to page closed
e2 = {'page':CourseURL('https://class.stanford.edu/courses/Medicine/SciWrite/Fall2013/courseware/875108aedf9549808fef9b1453c5a4ee/'),
      'event_type':'page_close',
      'current_location':(CourseURL('https://class.stanford.edu/courses/Medicine/SciWrite/Fall2013/courseware/875108aedf9549808fef9b1453c5a4ee/'),'')}

close_previous_page(e1)
close_previous_page(e2)

e3 = {'page':CourseURL('https://class.stanford.edu/courses/Medicine/SciWrite/Fall2013/courseware/000008aedf9549808fef9b1453c5a4ee/875108aedf9549808fef9b1453c5a4ee/'),
      'event_type':'seq_goto',
      'goto_dest':'3',
}

update_seq(e3)
simple_update(e3)
