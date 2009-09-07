import re

python_identifier = re.compile(r'^([a-zA-z]|_)(\w|_)?')

def get_iter_at_cursor(buffer):
    return buffer.get_iter_at_mark(buffer.get_insert)

def get_identifier_at_cursor(buffer):
    forward_iter = get_iter_at_cursor(buffer)
    backward_iter = get_iter_at_cursor(buffer)
    
    

