from ...utilities import db

def GetCourseraHashMap(vars, gen_anon):
    # DB connections
    # --------------
    s = vars['source']
    general_db_selector = db.Selector(s['host'], s['user'], s['password'], s['port'], s['general_db'])
    hm_db_selector = db.Selector(s['host'], s['user'], s['password'], s['port'], s['hash_mapping_db'])
    
    q = "SELECT * FROM hash_mapping"
    if vars['options']['debug']:
        users = general_db_selector.query("SELECT * FROM users limit 0,{}".format(vars['options']['num_users_debug_mode']))
        user_id_list = [u[gen_anon] for u in users]
        user_id_list_string = "','".join(user_id_list)
        q += " WHERE {} IN ('{}')".format(gen_anon, user_id_list_string)
    rows = hm_db_selector.query(q)
    
    if vars['source']['platform_format'] == 'coursera_1':
        map = {
            'map_forum': {row['forum_user_id']: row['user_id'] for row in rows},
            'map_general': {row['anon_user_id']: row['user_id'] for row in rows},
            'list_raw': [row['user_id'] for row in rows],
            'qls_general': ["'{}'".format(row['anon_user_id']) for row in rows],
            'qls_forum': ["'{}'".format(row['forum_user_id']) for row in rows],
        }
    else:
        map = {
            'map_forum': {row['user_id']: row['user_id'] for row in rows},
            'map_general': {row['session_user_id']: row['user_id'] for row in rows},
            'list_raw': [row['user_id'] for row in rows],
            'qls_general': ["'{}'".format(row['session_user_id']) for row in rows],
            'qls_forum': [str(row['user_id']) for row in rows],
        }
    
    return map