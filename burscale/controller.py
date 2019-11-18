import sys
import json
import time
import boto3
import logging
import requests
import datetime
from lb import *
from vm import *
import threading
from ec2 import *
from math import ceil
from monitor import *
from time import sleep
from pprint import pprint
from scaling_policy import *
from threading import Thread
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

requests.adapters.DEFAULT_RETRIES = 40

config_file = sys.argv[1]
config = json.loads(open(config_file).read().strip())
mu = config['mu']
default_weight = config['default_weight']
baseline = config['baseline']
btype = config['btype']
regtype = config['regtype']
image_id = config['image_id']
az = config['az']
sg = config['sg']
snid = config['snid']
key_name = config['keyname']
init = config['init']
duration = config['duration']
logfile = config['logfile']
balancer_id = config['balancer_id']
balancer_label = config['balancer_label']
balancer_host_name = config['balancer_host_name']
region_name = config['region_name']
lb_url = 'http://'+balancer_host_name+':26590'





logger = logging.getLogger("BSLog")
logger.setLevel(logging.INFO)
fh = logging.FileHandler(logfile)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

iids = []

procurements = []
_vm = []

instances= []
removed_instances = []

workers = []
od_workers = []
b_workers = []

json_lock = threading.Lock()

odLock = threading.Lock()
bLock = threading.Lock()

LEVEL_MAP = {
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.CRITICAL,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
    "NOTSET": logging.NOTSET
    }

class LBAttacher(Thread):
    def __init__(self, vm):
        super(LBAttacher, self).__init__()
        self.vm = vm
    def run(self):
        add_worker_to_lb(balancer_id,lb_url, self.vm)


class LBDetacher(Thread):
    def __init__(self, vm):
        super(LBDetacher, self).__init__()
        self.vm = vm
    def run(self):
        turn_off_worker(lb_url, self.vm)
        terminate_instance(self.vm.get_instance_id(), region_name)


def bring_procurements():
    attachers = []
    for inst_id in procurements:
        global _vm
        vm = VM(inst_id)
        attacher = LBAttacher(vm)
        _vm.append(vm)
        attacher.start()
        attachers.append(attacher)
    for attacher in attachers:
        attacher.join()

def bring_new_resource(num, vmtype=regtype, addToWorkers=True):
    logger.info("Requested {} instances".format(num))
    global image_id, az, sg, snid, key_name, region_name
    iids = create_instance(num=num, vmtype=vmtype, image_id=image_id, az=az, sg=sg, snid=snid, key_name=key_name)
    logger.info("Got {} instances".format(num))
    client = boto3.resource('ec2', region_name=region_name)
    attachers = []
    req = requests.Session()
    retries = Retry(total=15, backoff_factor=0.1, status_forcelist=[ 500, 502, 503, 504 ])
    req.mount('http://', HTTPAdapter(max_retries=retries))
    for inst_id in iids:
        logger.info("Starded adding instance {}".format(inst_id))
        while client.Instance(inst_id).state['Code'] !=16:
            sleep(0.1)
        while req.get("http://"+client.Instance(inst_id).public_dns_name, timeout=50).status_code !=200:
            sleep(1)
        vm = VM(inst_id)
        vm.set_weight(1)
        if not(vmtype.startswith("t")):            
            global od_workers
            if addToWorkers:
                odLock.acquire()
                od_workers.append(vm)
                odLock.release()
        else:
            global b_workers
            if addToWorkers:
                bLock.acquire()
                b_workers.append(vm)
                bLock.release()

        attacher = LBAttacher(vm)
        attacher.start()
        logger.info("Added instance {} to LB: ".format(inst_id))
        attachers.append(attacher)
    for attacher in attachers:
        attacher.join()

def remove_workers(num, vmtype):
    '''
    vmtype is either od or b
    '''
    if num > 0:
        if vmtype == "od" and num < len(od_workers):
            detachers = []
            for i in range(num):
                odLock.acquire()
                vm = od_workers.pop()
                odLock.release()
                detacher = LBDetacher(vm)
                detacher.start()
                detachers.append(detacher)
                logger.info("Removed instance {} from LB: ".format(vm.get_instance_id()))
            for detacher in detachers:
                detacher.join()
        elif vmtype == "b" and num < len(b_workers):
            detachers = []
            for i in range(num):
                bLock.acquire()
                vm = b_workers.pop()
                bLock.release()
                detacher = LBDetacher(vm)
                detacher.start()
                detachers.append(detacher)
                logger.info("Removed instance {} from LB: ".format(vm.get_instance_id()))
            for detacher in detachers:
                detacher.join()


if (__name__=='__main__'):
        bring_new_resource(num=init)
        logger.info("BurScale Started")
        od_excess = 0
        b_excess = 0
        excess_window = []
        while True:
            rate  = calc_arrival_rate(balancer_host_name, duration)
            od_k = len(od_workers)
            b_k = len(b_workers)
            R = ceil(rate/mu)
            od_excess = R  - od_k
            b_excess = scale(rate, mu) - R - b_k
            if od_excess > 0:
                Thread(target = bring_new_resource, args = (od_excess , regtype, True) ).start()
            elif od_excess < 0 :
                Thread(target=remove_workers, args=(abs(od_excess), "od")).start()

            if b_excess > 0:
                Thread(target = bring_new_resource, args = (b_excess , btype,True) ).start()
            elif b_excess < 0 :
                Thread(target=remove_workers, args=(abs(b_excess), "b")).start()

            excess_window.append(od_excess + b_excess)

            if len(excess_window) >= 3 and sum(excess_window[-3:] <= 1):
                bi = b_workers[0]
                default_weight = get_curr_weight(default_weight, baseline, bi)
                for oi in od_workers:
                    oi.set_weight(default_weight)
                    Thread(target=update_worker_attribute, args=(lb_url, oi, {})).start()
            else:
                if od_workers[0].get_weight() !=1:
                    for oi in od_workers:
                        oi.set_weight(1)
                        Thread(target=update_worker_attribute, args=(lb_url, oi, {})).start()

            time.sleep(duration)
