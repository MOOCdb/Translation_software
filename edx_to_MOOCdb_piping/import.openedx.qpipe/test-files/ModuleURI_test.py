import sys
import os

sys.path.insert(0, os.path.join( os.getcwd(), os.path.pardir))

from helperclasses import ModuleURI

MODULE_INLINE = ['input_i4x-MITx-6_002x-problem-H12P3_Opamps_and_Filter_Design_10_1',
                 'input_i4x-MITx-6_002x-problem-4b92e25c8dd24d928d47a63adbc1f1f6_5_1',
                 'input_i4x-MITx-6_002x-problem-L2Node0_2_1_dynamath',
                 '"input_i4x-MITx-6_002x-problem-S7E2_Graphs_2_1',
                 'input_i4x-MITx-6_002x-problem-S23E1_Non-Inverting_Amplifier_2_1',
                 'input_i4x-MITx-6_002x-problem-S23E1_Non-Inverting_Amplifier_2_1=R&input_i4x-MITx-6_002x-problem-First-order_Transients_3_1'] 

MODULE_EVENT_TYPE = ['i4x://MITx/6.002x/problem/Q2Final2012',
                     '/courses/MITx/6.002x/2013_Spring/modx/i4x://MITx/6.002x/problem/Op_Amps/problem_get',
                     '/courses/MITx/6.002x/2013_Spring/jump_to/i4x://MITx/6.002x/course/2013_Spring/',
                     '/courses/MITx/6.002x/2013_Spring/jump_to/i4x://MITx/6.002x/discussion/discussion_ada9b41788ab',
                     '/courses/MITx/6.002x/2013_Spring/modx/i4x://MITx/6.002x/problem/0d4f2b54bcd34f74a6bd522e3ee013a6/problem_check',
                     '/courses/MITx/6.002x/2013_Spring/submission_history/lyla@edx.org/i4x://MITx/6.002x/problem/1d57e8ae8ade4d88b92481844e063696',
                     '/courses/MITx/6.002x/2013_Spring/modx/i4x://MITx/6.002x/sequential/Week_4_Tutorials/goto_position'
]

BAD_MODULES = ['input_i4x-MITx-6_002x-problem-Mosfet_Amplifier_2_1=.5&input_i4x-MITx-6_002x-problem-Mosfet_Amplifier_3_1=1.1&input_i4x-MITx-6_002x-problem-Mosfet_Amplifier_4_1=&input_i4x-MITx-6_002x-problem-Mosfet_Amplifier'
               ]

mit_6002x = MODULE_INLINE + MODULE_EVENT_TYPE + BAD_MODULES
solar_fall_2013 = ['input_i4x-Engineering-Solar-problem-bc31c9ab2dab4bba8ad8f716f8ecf8d5_2_1_choice_2',
                   'input_i4x-Engineering-Solar-problem-bc31c9ab2dab4bba8ad8f716f8ecf8d5',
                   'input_i4x-Engineering-Solar-problem-222c588f6afe48ea8eac46af8795039f_2_1%5B%5D=choice_0'] 

def test(s):
    print '** Input : %s'%s
    module = ModuleURI(s)
    print '- Full URI :: %s'% str(module)
    print '- Relative URI :: %s'% module.get_relative_uri()
    print '- Top level URI :: %s'% module.get_top_level_uri()
    print '- Module ID :: %s' % module.module_id
    print '- Name :: %s' % module.get_name()
    print '- Category :: %s' % module.category
    print '- Rescued answer :: %s '% module.rescued_answer
    print '- Action :: %s' % module.action

def run_test(l):
    for s in l:
        test(s)

if __name__ == '__main__':
    with open('test-results.org','w') as f:
        sys.stdout = f
        print '* Testing 6002x'
        run_test(mit_6002x)
        print '* Testing Solar'
        run_test(solar_fall_2013)

        
