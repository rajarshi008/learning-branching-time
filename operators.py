# defining global operator constants

ctl_boolean = ['&', '|', '->', '!']
ctl_unary = ['EG', 'EF', 'EX', 'AG', 'AF', 'AX', '!']
ctl_binary = ['&', '|', '->', 'EU', 'AU']
ctl_operators = ctl_unary + ctl_binary


atl_boolean = ['&', '|', '->', '!']
atl_temporal = ['G', 'F', 'X', 'U']
atl_unary = ['G', 'F', 'X','!']
atl_binary = ['&', '|', '->', 'U']
atl_operators = atl_unary + atl_binary