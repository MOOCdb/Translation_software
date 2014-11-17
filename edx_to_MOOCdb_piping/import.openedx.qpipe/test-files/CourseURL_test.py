import sys
import os

sys.path.insert(0, os.path.join( os.getcwd(), os.path.pardir))

from helperclasses import CourseURL

# Sample of courseware URLs
CoursewareURLs = [ 'https://54.243.37.197/courses/MITx/6.002x/2013_Spring/courseware/Week_1/Week_1_Tutorials/',
                   'https://courses.edx.org/courses/MITx/6.002x/2013_Spring/courseware/Week_10/Homework_10/#',
                   ' https://courses.edx.org/courses/MITx/6.002x/2013_Spring/courseware/Week_12/wk10_CS/?title=Here%27s+the+link+to+S10E2+and+Mosfet+mirrors&follow=on',
                   'https://courses.edx.org/courses/MITx/6.002x/2013_Spring/courseware/Week_13/Op_Amps_Positive_Feedback/10'
]
                   
BookURLs = ['https://courses.edx.org/courses/MITx/6.002x/2013_Spring/book/0/214',
            'https://courses.edx.org/courses/MITx/6.002x/2013_Spring/book/0/',
            'https://courses.edx.org/courses/MITx/6.002x/2013_Spring/book/0/0',
            'https://www.edx.org/courses/MITx/6.002x/2013_Spring/book/0/'
]


RelativeURLs = [
                '/courses/MITx/6.002x/2013_Spring/about/+json.field+',
                '/courses/MITx/6.002x/2013_Spring/book/0/1002',
                '/courses/MITx/6.002x/2013_Spring/courseware/d6400fa12fbc44ea8328db31f6c07182/b85fb22ac3b4422d9559282bf5b4ffce/'
]

pathological = ['/courses/MITx/6.002x/2013_Spring/about//c4x/MITx/6.002x/asset/images_about_agarwal-small.jpg',
                'https://www.edx.org/courses/MITx/6.002x/2013_Spring/courseware/Week_1/Week_1_Tutorials/#',
                'https://www.edx.org/courses/MITx/6.002x/2013_Spring/courseware/Week_2/Lab_2/1/undefined?zoneid=27&amp;id=lfkgmnnajiljnolcgolmmgnecgldgeld&amp;v=0.17.4&amp;refresh=60',
                'https://www.edx.org/courses/MITx/6.002x/2013_Spring/courseware/Week_2/Linearity_and_Superposition//1',
                'https://www.edx.org/courses/MITx/6.002x/2013_Spring/courseware/Week_2/Linearity_Thevenin_and_Norton_Digital/answer_i4x-MITx-6_002x-problem-f13a01a4bdc14dd98acbb5ca4c34032e_2_3',
                'https://www.edx.org/courses/MITx/6.002x/2013_Spring/courseware/Week_3/Lab_3/solution_i4x-MITx-6_002x-problem-Logic_Gate_Implementation_solution_1',
                'x_module',
                '/courses/MITx/6.002x/2012_Fall/; /static/images/favicon.c074c912999f.ico', # Comes as an event type
                '/courses/MITx/6.002x/2012_Fall/wiki/math-review/${static.url(\'js/html5shiv.js\')}/',
                '/courses/MITx/6.002x/2012_Fall/[object Object]://www.mytoolsapp.info/worker/init.js',
                ]


def test(instance):
    print str(instance)
    print '- Base URL :: %s' % instance.get_base_url()
    print '- Unit :: %s'% instance.unit
    print '- Subunit :: %s'% instance.subunit
    print '- Panel :: %s'% instance.seq
    if instance.booknum:
        print '- Book :: %s and page %s' % (instance.booknum, instance.page)
        instance.set_page(42)
    instance.set_seq(42)
    print '- After operations :: %s'%instance

def test_urls(urls):
    for s in urls:
        print '** Input : %s'%s
        test(CourseURL(s))

def test_bad_urls(BadURLs):
    print '* Testing bad URLs'
    for s in BadURLs:
        print '\n'
        print s
        print CourseURL(s)

if __name__ == '__main__':
    with open('test-results.org','w') as f:
        sys.stdout = f
        print '* Courseware URLs'
        test_urls(CoursewareURLs)
        print '* Relative URls'
        test_urls(RelativeURLs)
        print '* Book URLs'
        test_urls(BookURLs)
        print '* Pathological URLs'
        test_urls(pathological)
       
        
        

        
    
    


