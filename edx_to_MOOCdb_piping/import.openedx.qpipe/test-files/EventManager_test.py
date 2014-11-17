import os
import sys
import datetime

sys.path.insert(0, os.path.join(os.getcwd(), os.pardir) )

from eventmanager import EventManager
from events import Event

def parse_time(s):
    return datetime.datetime.strptime(s,'%Y-%m-%d %H:%M:%S')

EVENTS = [ Event({'_id':1, 'anon_screen_name':'A', 'time':parse_time('2013-11-10 06:00:00')}),
           Event({'_id':2, 'anon_screen_name':'B', 'time':parse_time('2013-11-10 06:00:00')}),
           Event({'_id':3, 'anon_screen_name':'A', 'time':parse_time('2013-11-10 06:05:00')}),
           Event({'_id':4, 'anon_screen_name':'B', 'time':parse_time('2013-11-10 06:10:00')}),
           Event({'_id':5, 'anon_screen_name':'A', 'time':parse_time('2013-11-10 06:10:00')})]


if __name__ == '__main__':
    manager = EventManager()
    for event in EVENTS:
        e = manager.stage_event(event)
        if e:
            print ','.join([e['_id'], e['anon_screen_name'], str(e.duration)]) 
        

# Expected output is:
#  1,A,5
#  2,B,10
#  3,A,5
