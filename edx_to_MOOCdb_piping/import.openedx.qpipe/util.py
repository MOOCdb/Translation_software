import datetime
import re

# Loads a list of functions from a given module,
# the names of functions to load given in config_file
# Test : OK
def load_functions(config_file,module):

    f = open(config_file,'r')
    func_list = []

    try:
        for l in f: 
            func_name = l.strip()

            if not func_name:
                continue

            func = getattr(module,func_name)
            func_list.append(func)

    except AttributeError:
        print '[load_functions] Attribute error : <' + func_name + '> not in module <' + str(module) + '>'

    finally:
        f.close()
        return func_list


# Loads a function from its name
def load_function(module, func_name):
    try:
        func_name = func_name.strip()
        return getattr(module,func_name)

    except AttributeError:
        print '[load_function] Module ' + str(module) + ' has no function <' + func_name + '>'  
        

# Loads a set of rules from a text file
# Returns a list of (<field_name>, <compiled regexp>, <list of functions>)
def load_rules(config_file,module=None):

    f = open(config_file,'r')
    rules_list = []

    for l in f:

        if l.strip() == '':
            #print 'Empty line !'
            continue

        text_rule = l.split(',')
        print text_rule

        field = text_rule[0].strip()
        regexp = re.compile(text_rule[1].strip())
        function = None
        
        # If the rule has no function associated, 
        # it is interpreted as a filter. This is done
        # by assigning a lambda that returns False as rule function
        if len(text_rule) == 2:
            print '[load_rules] Loading filter rule'
            function = (lambda x:False)

        else:
            function = load_function(module,text_rule[2].strip())

        rules_list.append({'field':field, 'regexp':regexp, 'function':function})

    f.close()
    print '[load_rules] Loading successful'
    return rules_list

# Applies a set of rules to an array
def apply_rules(rules, array):
    
    for rule in rules: 
        if rule['regexp'].search(str(array[rule['field']])):
            # print 'Applying rule : ' + str(rule['field']) + ' ' + str(rule['regexp'].pattern) 
            return rule['function'](array)

    # print 'No rules applied to ' + str(array)
    return None

