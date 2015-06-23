def block_sql_command(conn, cursor, command, data, block_size):
    last_block = False
    current_offset = 0
    while last_block == False:
        print "CURRENT_OFFSET:"
        print current_offset
        print "offset + block size"
        print current_offset + block_size
        print "length of data:"
        print len(data)
        if current_offset + block_size < len(data):
            print "normal"
            block = data[current_offset:current_offset+block_size]
        else:
            print "last"
            block = data[current_offset:]
            last_block = True
        print "BLOCK:"
        print block
        if block:
            data_str = str(block)[1:-1]
            grounded_command = command % (data_str)
            print "GROUNDED COMMAND:"
            print grounded_command
            #cursor.execute(grounded_command)
            #conn.commit()
            current_offset += block_size

data = range(50)
modify_invalids = '''
        UPDATE submissions
        SET validity = 0
        WHERE submission_id in (%s)'''
block_sql_command("", "", modify_invalids, data, 5)
