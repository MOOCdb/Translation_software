import re

INPUT = '6002x_problem_ids.org' 
OUTPUT = 'pb-id-extraction-results.org'

REGEXP = re.compile('-problem-(?P<id>.+(?P<tail>_[0-9]_[0-9]))$')

finput = open(INPUT,'r')
foutput = open(OUTPUT,'w')

row = '|{}|{}|{}|\n'

header = row.format('problem_id','id','tail')

foutput.write('* Matches\n')
foutput.write(header)

matching_errors = []

for line in finput:
    problem_id = line.strip()
    match = REGEXP.search(problem_id)
    try:
        new_row = row.format(problem_id, match.group('id'), match.group('tail'))
        foutput.write(new_row)
    except Exception as e:
        matching_errors.append(problem_id)


foutput.write('* Errors\n')
for problem_id in matching_errors:
    foutput.write('- '+ problem_id + '\n')

print 'Done !'
finput.close()
foutput.close()


