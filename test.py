import time
s = 0
m = 0
h = 0
while True:
    if s > 59:
        s = 0
        m = m+1
    
    if m > 59:
        h = h+1
        m = 0
        s = 0
    
    sec = "{:02d}".format(s)
    min = "{:02d}".format(m)
    hrs = "{:02d}".format(h)
    print(hrs+":"+min+":"+sec)
    s = s+1
    time.sleep(1)