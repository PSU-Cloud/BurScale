# BurScale
## Warning: This is not a production-ready tool!
BurScale is an autoscaling system which uses a combination of regular and burstable virtual machine instances to save in costs.
BurScale is published as a [research paper](https://mrata.github.io/files/burscale.pdf) in ACM Symposium on Cloud Computing 2019 ([SoCC'19](https://acmsocc.github.io/2019/)).
You can use the following bibTex to cite the paper:
```
@inproceedings{Baarzi:2019:BUB:3357223.3362706,
 author = {Baarzi, Ataollah Fatahi and Zhu, Timothy and Urgaonkar, Bhuvan},
 title = {BurScale: Using Burstable Instances for Cost-Effective Autoscaling in the Public Cloud},
 booktitle = {Proceedings of the ACM Symposium on Cloud Computing},
 series = {SoCC '19},
 year = {2019},
 isbn = {978-1-4503-6973-2},
 location = {Santa Cruz, CA, USA},
 pages = {126--138},
 numpages = {13},
 url = {http://doi.acm.org/10.1145/3357223.3362706},
 doi = {10.1145/3357223.3362706},
 acmid = {3362706},
 publisher = {ACM},
 address = {New York, NY, USA},
 keywords = {autoscaling, burstable instances, cloud computing, resource provisioning},
}
```

## How to use?
BurScale is implemented on top of AWS, so all the instructions bellow assume that you're operating on AWS.
BurScale relies on two components: loadbalancer configurator and burscale controller:
### Loadbalancer Configuration
To deploy BurScale, you have to make sure that your ingress loadbalancer exposes enough endpoints for BurScale such as adding/removing node, updating the dispatching policy, and collecting the statistics.

For example, if you use Nginx as your loadbalancer, you may use [loadcat](https://github.com/PSU-Cloud/BurScale/loadcat) which is a loadbalancer configurator tool for Nginx. We recommend to use our own fork of loadcat which supports different types of instances including burstable instances. 
To run the `loadcat` daemon along with your loadbalancer node, run the binary:
```
./loadcat &
```
This will run the loadcat daemon and exposes port 26590 for BurScale usage.
Before deploying the BurScale controller, you have to create/configure a loadbalancer using loadcat. Browse `LOADBALABCER-DNS:26590/balancers/new` to create and configure the loadbalancer. For more information please refer the [loadcats documentation](https://github.com/mahmud-ridwan/loadcat). 
#### BurScale controller
After configuring the loadbalancer, your can deploy the burscale controller. 
##### BurScale configuration file
In order to deploy BurScale, you have to provide a configuratoin file which contains necessary configurations for BurScale controller:
```
    "mu": The service rate of the application.
    "default_weight": The initial weight that is used for loadbalancer.
    "baseline": The baseline CPU utilization for burstable instances.
    "init": Initial number of regular instances for the cluster.
    "btype": The type of burstable instances that are used.
    "regtype": The type of regular instances that are used.
    "image_id": The ID of AMI that is used for the application.
    "az": The AWS availablity zone that the application is deployed.
    "sg": The AWS security group that the application is deployed.
    "snid": The AWS subnet ID that the application is deployed.
    "keyname": The AWS access key name that the instances are created.
    "duration": The window size (in seconds) in which the autoscaler makes descision.
    "balancer_id": The balancer ID that loadcat creates.
    "balancer_host_name": The DNS for the loadbalancer.
    "balancer_label": The loadbalancer's label created by loadcat.
    "region_name": AWS region that the application is deployed.
    "logfile": BurScale's logging file name.
```
##### Deploy BurScale
Once the loadbalancer is created and configured and also the configuratiotion file for BurScale is ready, you can deploy the BurScale controller. You can either use a docker image or directly use the source files.
###### Docker Image
A `Dockerfile` is provided for ease of use. Follow these instructions to build, push, pull, and finally run the docker container containing BurScale controller.

Build:
```
docker build -t <your-username>/burscale:latest .
```
Push:
```
docker push <your-username>/burscale:latest
```
On your loadbalancer node, pull the image:
```
docker pull <your-username>/burscale:latest
```
Finally run the container:
```
docker run -v ./config.json:config.json burscale config.json
```

###### Deploy from source
If you want to use the source directly, follow the instructions bellow:
```
pip3 install -r requirements.txt
cd ./burscale
python3 controller.py config.json
```







