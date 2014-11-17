import sys
import os

sys.path.insert(0, os.path.join( os.getcwd(), os.path.pardir))

from extractor import CSVExtractor

EDX_TRACK_EVENT = os.path.join( os.getcwd(), 'data/EdxTrackEvent.csv')
ANSWER = os.path.join(os.getcwd(), 'data/Answer.csv')
CORRECT_MAP = os.path.join(os.getcwd(), 'data/CorrectMap.csv')

if __name__ == '__main__': 
    extractor = CSVExtractor(edx_track_event=EDX_TRACK_EVENT, answer=ANSWER, correct_map=CORRECT_MAP)
    for event in extractor:
        print '| {} | {} | {} |'.format(event['answer_identifier'], event['answer'], event['correctness'])


    
