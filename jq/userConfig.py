
userconfig = {
    "if_load_data":True,
    "start":"2020-01-01",
    "end":"2022-01-01",
    "start_cash":100000000
}

# userconfig = {
#     "if_load_data":True,
#     "start":"2019-01-01",
#     "end":"2019-06-30",
#     "start_cash":100000000
# }

stock_column_tuple = (
    #'ts_code', 'date', 'open', 'close'是必需的
    ('ts_code', 'U11', 0),
    ('date', 'datetime64[s]', 1), 
    ('open', 'float32', 3),
    ('high', 'float32', 5),
    ('low', 'float32', 7),
    ('close', 'float32',9),
    ('pre_close', 'float32', 10),
    ('change', 'float32', 11),
    ('vol', 'int32', 12),
    ('amount', 'float32', 13)
)

index_column_tuple = (
    #'ts_code', 'date', 'open', 'close'是必需的
    ('ts_code', 0),
    ('date', 1),
    ('close', 2),
    ('open', 3),
    ('high', 4),
    ('low', 5)
)


db_config = {
    "host": "localhost",
    "user": "root",
    "password": "yourpassword",
}
