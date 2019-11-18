import boto3

class VM:
    def __init__(self, instance_id):
        self.instance_id = instance_id
        self.instance_ip = self.get_instance_ip()
        self.worker_id = None
        self.vmtype = self.get_instance_type()
        self.weight = 1

    def set_weight(self, w):
        self.weight = w
    def get_weight(self):
        return self.weight
    def get_instance_id(self):
        return self.instance_id

    def set_worker_id(self, id):
        self.worker_id = id

    def get_worker_id(self):
        return self.worker_id

    def set_instance_type(self, vmtype):
        self.vmtype = vmtype
    def get_instance_type(self):
        client = boto3.client('ec2')
        response = client.describe_instances(InstanceIds=[self.instance_id])
        if response['Reservations'][0]['Instances'][0]['InstanceType'].startswith('t2'):
            return 'burst'
        return 'ondemand'


    def get_instance_ip(self, ip_type='PrivateIpAddress'):
        '''
        returns the public or private ip address of the instance.
        to get the public ip address, set ip_type to "PublicIp"
        to get the private ip address (default) set ip_type to PrivateIpAddress
        '''
        client = boto3.client('ec2')
        response = client.describe_instances(InstanceIds=[self.instance_id])
        return response['Reservations'][0]['Instances'][0]['NetworkInterfaces'][0][ip_type]

    def get_instance_credit_balance(self):
        client = boto3.client('cloudwatch')
        response = client.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='CPUCreditBalance',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': self.instance_id
            },
        ],
        StartTime=datetime.datetime.now()- datetime.timedelta(minutes=5),
        EndTime=datetime.datetime.now(),
        Period=300,
        Statistics=[
            'SampleCount','Average','Sum','Minimum','Maximum'
        ],
        )
        return response['Datapoints'][0]['Average']
    def get_instance_credit_usage(self):
        client = boto3.client('cloudwatch')
        response = client.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='CPUCreditUsage',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': self.instance_id
            },
        ],
        StartTime=datetime.datetime.now()- datetime.timedelta(minutes=5),
        EndTime=datetime.datetime.now(),
        Period=300,
        Statistics=[
            'SampleCount','Average','Sum','Minimum','Maximum'
        ],
        )
        return response['Datapoints'][0]['Average']

def get_instance_cpu_util(self):
        client = boto3.client('cloudwatch')
        response = client.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='CPUUtilization',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': self.instance_id
            },
        ],
        StartTime=datetime.datetime.now()- datetime.timedelta(minutes=5),
        EndTime=datetime.datetime.now(),
        Period=60,
        Statistics=[
            'SampleCount','Average','Sum','Minimum','Maximum'
        ],
        )
        return response['Datapoints'][0]['Average']
