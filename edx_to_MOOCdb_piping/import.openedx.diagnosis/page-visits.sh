# Give some visit counts based on the collected URL change events.

# $PAGE_VISITS :
# --------------
# 23   a/b/c
# 2    e/f/g
# 3445 h/i/j
# ...

# To avoid noise, keep only URLs that have more than 100 visits.
# This gives all distinct URLs accessed.
grep -r ' [0-9][0-9][0-9] ' $PAGE_VISITS > $PAGE_VISITS_CUTOFF

# Get the 10 most accessed ULRs
cat $PAGE_VISITS | sort -rn | head '-'$HOW_MANY > $MOST_VISITED

# Get the 10 most visited of a category
WEEK=''
SEQUENCE='courseware/[^/]*/[^/]*/'
BOOK=''
WIKI=''

grep $CATEGORY_REGEXP $PAGE_VISITS | sort -rn | head '-'$HOW_MANY > $CATEGORY_MOST_VISITED



# Get all accessed sequence URLs, and order them by access count

