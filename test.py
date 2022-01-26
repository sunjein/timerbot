from datetime import datetime

def time_to_int(dt):
    basetime = datetime(2000,1,1,hour=0,second=0,microsecond=0,tzinfo=None)
    diff = dt - basetime
    return int(diff.total_seconds())


print(time_to_int(datetime.now()))