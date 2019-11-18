import requests
import json
def add_worker_to_lb(balancer_id, lb_url, vm):
    '''
    add a new worker to laod balancer.
    The attr_dict must contain backup and down attrs and both should be set to false
    weight attr also is in this data structure and default value is 1
    '''
    uri = "/balancers/"+balancer_id+"/servers/new"
    URL = lb_url + uri
    data = {}
    data["settings.address"] = vm.get_instance_ip()
    print(data)
    data["label"] = vm.get_instance_id()
    print(data)
    print(URL)
    r = requests.post(url=URL, data = data)
    worker_id = r.text.strip("\n")
    vm.set_worker_id(worker_id)
    print(r.text)
    print(r.status_code)
    assert r.status_code == 200
    #update
    data["settings.weight"]= vm.get_weight()
    data["settings.availability"] = "available"
    update_worker_attribute(lb_url,vm, data)
    #json_lock.acquire()
    with open('workers.json') as json_file:
        try:
            json_data = json.load(json_file)
        except:
            json_data = {}
            json_data['workers'] = []
        json_data['workers'].append(vm.__dict__)

    with open('workers.json', 'w') as json_file:
        json.dump(json_data,json_file)
    #json_lock.release()
    return r.text

def update_worker_attribute(lb_url,vm, attr_dict={}):
    '''
    updates the following:
    label: any arbitrary string
    settings.address: (private) ip address of the instance
    settings.weight: integer value for wieght
    settings.availability: available, backup, unavailable
    '''
    uri = "/servers/"+vm.get_worker_id()+"/edit"
    URL = lb_url + uri
    data = attr_dict
    data["settings.address"] = vm.get_instance_ip()
    data["label"] = vm.get_instance_id()
    data["settings.vmtype"] = vm.get_instance_type()
    data["settings.weight"]= vm.get_weight()
    r = requests.post(url=URL, data=data)

    assert (r.status_code == 200)
    return
def turn_off_worker(lb_url,vm):
    return update_worker_attribute(lb_url, vm , {"settings.availability":"unavailable"})

def turn_on_worker(vm):
    return update_worker_attribute(lb_url,vm , {"settings.availability":"available"})

def get_vm_status(vm, stat):
    '''
    stat can be one of the following:
    -SettingsAvailability
    -SettingsWeight
    '''
    uri = "/servers/"+vm.get_worker_id()+"/status"
    r = requests.get(URL)
    return json.loads(r.text)[stat]

def change_lb_method(lb_method):
    '''
    lb_method should be one of the following:
    -round-robin
    -least-connections
    -source-ip
    '''
    uri = "/balancers/"+balancer_id+"/edit"
    URL = lb_url+uri
    data = {"label":balancer_label, "settings.hostname":balancer_host_name, "settings.port":80, "settings.protocol":"http", "settings.algorithm":lb_method}

    print(URL)
    print(data)
    r = requests.post(url=URL, data=data)
    print(r.status_code)
    assert r.status_code == 200
    return

def generate_workers(iids):
    for instance_id in iids:
        instances.append(VM(instance_id))
    for vm in instances:
        add_worker_to_lb(vm,1)

def load_workers():
    instances = []
    with open('workers.json') as json_file:
        data = json.load(json_file)
        for worker in data['workers']:
            vm = VM(worker['instance_id'])
            vm.set_worker_id(worker['worker_id'])
            vm.set_instance_type(worker['wmtype'])
            instances.append(vm)
    return instances

def create_balancer(balancer_attr={"label":"mybalancer", "settings.hostname":"balancer_host_name",
"settings.port":80, "settings.protocol":"http", "settings.algorithm":"round-robin"}):
    '''
    balancer_attr should contain the following:
    -label: balancer Label
    -settings.hostname: The hostname for balancer
    -settings.port: The port of balancer
    -settings.protocol: The protocol is used; http or https
    -settings.algorithm: The balancing method: round-robin,least-connections, source-ip
    '''
    uri = "/blancers/new"
    URL = lb_url + uri


def get_upstream_status():
    uri = "api/1/http/upstreams/appservers/"
    URL = lb_url + uri
    r = requests.get(url=URL)
    assert r.status_code == 200
    return r.text


def get_all_workers():
    uri = "api/1/http/upstreams/appservers/"
    URL = lb_url + uri
    r = requests.get(url=URL)
    assert r.status_code == 200
    return r.text
