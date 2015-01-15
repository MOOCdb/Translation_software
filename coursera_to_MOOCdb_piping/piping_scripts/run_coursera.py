'''
To run:
cd <parent of the directory containing this file>
python -m piping_scripts.run_coursera
'''

from main import *

vars = {
    'source': {
        'platform_format': '',
        'course_id': '',
        'course_url_id': '',
        'host': '',
        'user': '',
        'password': '',
        'port': 3306,
        'hash_mapping_db': '',
        'general_db': '',
        'forum_db': '',
    },
    
    'core': {
        'host': '',
        'user': '',
        'password': '',
        'port': 3306,
    },
    
    'target': {
        'host': '',
        'user': '',
        'password': '',
        'port': 3306,
        'db': '',
    },
    
    'options': {
        'log_path': None,
        'log_to_console': True,
        'debug': False,
        'num_users_debug_mode': 200,
    },
}

main(vars)