import boto3


def create_instance(vmtype='m5.large', num=1, image_id="", az="", sg="", snid="", key_name=""):
    ec2 = boto3.resource('ec2', region_name="us-east-2")
    instance = ec2.create_instances(
    ImageId=image_id,
    InstanceType=vmtype,
    KeyName=key_name,
    MaxCount=num,
    MinCount=1,
    Monitoring={
        'Enabled': True
    },
    Placement={
        'AvailabilityZone': az,
    },
    SecurityGroupIds=[
        sg,
    ],
    SubnetId=snid,
    DisableApiTermination=False,
    InstanceInitiatedShutdownBehavior='stop',
    TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'webserver_b'
                },
            ]
        },
    ]
    )
    print(instance)
    # print(instance[0].instance_id)
    return [instance[i].instance_id for i in range(len(instance))]

def terminate_instance(instance_id, region_name):
    client = boto3.client('ec2', region_name=region_name)
    response = client.terminate_instances(
    InstanceIds=[
        instance_id,
    ],
    )

def stop_instance(instance_id, region_name):
    client = boto3.client('ec2', region_name=region_name)
    response = client.stop_instances(
    InstanceIds=[
        instance_id,
    ],
    Force=True
    )
def start_instance(instance_id, region_name):
    client = boto3.client('ec2', region_name=region_name)
    response = client.start_instances(
    InstanceIds=[
        instance_id,
    ]
    )
