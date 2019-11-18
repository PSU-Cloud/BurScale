import logging
import requests
from ec2 import *
from time import sleep
from pprint import pprint
from threading import Thread
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
requests.adapters.DEFAULT_RETRIES = 40

LEVEL_MAP = {
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.CRITICAL,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
    "NOTSET": logging.NOTSET
    }

logger = logging.getLogger("ASLog")
logger.setLevel(logging.INFO)
fh = logging.FileHandler("my.log")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)


stopped_instances = []

def launch_instances(num, vmtype="m5.large"):
    client = boto3.resource('ec2', region_name="us-east-2")
    req = requests.Session()
    retries = Retry(total=15, backoff_factor=0.1, status_forcelist=[ 500, 502, 503, 504 ])
    req.mount('http://', HTTPAdapter(max_retries=retries))
    for i in range(num):
        logger.info("====================================================")
        logger.info("Starded launching instance number {}".format(i))
        inst_id = create_instance(num=1, vmtype=vmtype)[0]
        logger.info("instance number {0} has instance id {1}".format(i, inst_id))
        while client.Instance(inst_id).state['Code'] !=16:
            sleep(0.1)
        while req.get("http://"+client.Instance(inst_id).public_dns_name, timeout=50).status_code !=200:
            sleep(1)
        logger.info("Launched instance {0} with instance id {1} to LB: ".format(i,inst_id))

        sleep(2)
        logger.info("Stopping the instance for later usage")
        stop_instance(inst_id)
        stopped_instances.append(inst_id)
        sleep(2)


def start_instances():
    client = boto3.resource('ec2', region_name="us-east-2")
    req = requests.Session()
    retries = Retry(total=15, backoff_factor=0.1, status_forcelist=[ 500, 502, 503, 504 ])
    req.mount('http://', HTTPAdapter(max_retries=retries))
    logger.info("Starting instances...")
    for inst_id in stopped_instances:
        logger.info("#############################################################")
        logger.info("Started starting instance {}".format(inst_id))
        start_instance(inst_id)
        while client.Instance(inst_id).state['Code'] !=16:
            sleep(0.1)
        while req.get("http://"+client.Instance(inst_id).public_dns_name, timeout=50).status_code !=200:
            sleep(1)
        logger.info("Started instance with instance id {} to LB: ".format(inst_id))
        sleep(2)


if __name__=="__main__":
    logger.info("************************************************")
    logger.info("Program Started")
    launch_instances(30)
    start_instances()
