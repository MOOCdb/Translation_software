import sys
import os


sys.path.insert(0, os.path.join( os.getcwd(), os.path.pardir))
from events import Event
from helperclasses import CurationHelper, ModuleURI, CourseURL

url1 = CourseURL('https://courses.edx.org/courses/MITx/6.002x/2013_Spring/courseware/Week_10/Homework_10/1')
url2 = CourseURL('https://courses.edx.org/courses/MITx/6.002x/2013_Spring/courseware/Week_10/Homework_10/2')
url3 = CourseURL('https://courses.edx.org/courses/MITx/6.002x/2013_Spring/courseware/Week_13/Op_Amps_Positive_Feedback/10')

module1 = ModuleURI('input_i4x-MITx-6_002x-problem-H12P3_Opamps_and_Filter_Design_10_1')
module2 = ModuleURI('input_i4x-MITx-6_002x-problem-H12P3_Opamps_and_Filter_Design')
module3 = ModuleURI('i4x://MITx/6.002x/problem/Q2Final2012')

inputs = [(module1, Event({'url_id':1, 'page':url1, 'resource_id':1})),
          (module2, Event({'url_id':2, 'page':url2, 'resource_id':2})),
          (module2, Event({'url_id':1, 'page':url1, 'resource_id':3})),
          (module3, Event({'url_id':3, 'page':url3, 'resource_id':4}))] 

if __name__ == '__main__':

    print os.getcwd()
    h = CurationHelper(os.getcwd())
    for module, event in inputs:
        h.add_candidate_resource(module, event)
        h.add_curation_hint(module, event)

    print h.candidate_resources
    h.serialize()
