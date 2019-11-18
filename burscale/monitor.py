import time
import requests
from vm import *

URI = "/basic_status"''
perv_val = 0

def calc_arrival_rate(lb_url, duration):
    res = requests.get("http://"+lb_url + URI).text.split()
    curr_val = int(res[res.index("Reading:")-1])
    global perv_val
    reqs = curr_val - perv_val - 1
    rate = reqs/duration
    perv_val = curr_val
    return rate

def get_curr_weight(default_weight, baseline, bi):
    if bi.get_instance_cpu_util() > baseline:
        return default_weight+1

if __name__ == "__main__":
    while True:
        rate  = calc_arrival_rate()
        print(rate)
        time.sleep(DURATION)
