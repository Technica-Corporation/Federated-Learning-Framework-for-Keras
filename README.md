# Federated Learning Framework for Keras
This repository houses the codebase for Technica's Jetson A.I Certification submission. It also doubles as a generalized Keras focused Federated Learning framework designed to take advantage of Nvidia's Jetson Device ecosystem. 

The codebase abstracts common Federated Learning infrastructure in order to give users the ability to create and manage Nvidia Jetson devices, at scale, for the objective of Federated Learning. The framework has been tested with the Cybersecurity dataset for Anomaly Detection, [BETH](https://www.kaggle.com/datasets/katehighnam/beth-dataset?resource=download), but can be applied to other datasets or even organic data from within a user's network

## Federated Learning
Federated Learning is a distributed machine learning technique introduced by Google (https://ai.googleblog.com/2017/04/federated-learning-collaborative.html). Models are trained in parallel on their own set of data. Model updates are sent to a centralized aggregation service and redistributed. This allows each model to gain from the data and learning at the other locations. Since no data is sent to the central location, this approach provides greater privacy than centralized learning techniques.

In this project, we have applied federated learning to anomaly detection in a cybersecurity use case. The federated approach allows data to remain private on each Jetson device while the resultant model benefits from data gathered at each location.

## Tech Stack
In order to build and run the application locally, the following dependencies must be present on the local machine:

 1. Ansible - Creates and manages Federated Learning Infrastructure
 2. Docker - Used to automate Federated Learning environment 
 3. MQTT - Messaging protocol used to distribute data across Federated Learning nodes
 4. Tensorflow (Keras) - ML library used as runtime prediction/training environment 

A custom made library, dl_mqtt_clients, is also bundled with the codebase and is used to instantiate either a Prediction, Training, or Manager Python object. Each of which serve a role in the Federated Learning Process. 

## Framework Architectural Components 
A variety of Software components comprise the framework. These include:

 - Mosquito MQTT Broker
 - Federated Learning Management Service (dl_mqtt_clients)
 - Federated Learning Prediction Service (dl_mqtt_clients)
 - Federated Learning Training Service (dl_mqtt_clients)
 - Data Generator 

The key to the successes of the framework is the dl_mqtt_clients Python library. This library abstracts the machine learning functions required for model prediction, training, fitting, and merging from the user. What this means is that the user can use pretrained models with the services in the Framework to achieve Federated Learning. It is as simple as modifying some simple configuration parameters for the runtime environment and then scaling it out! The important part to note is that data must be transferred between nodes via MQTT. An additional data generator utility has been added to the framework to make streaming data via MQTT to nodes in the cluster for demonstration purposes. 

![alt text](images/Demo_Architecture.png?raw=true "Title")

## Getting Started 
Before using the framework, users must first setup their environment. From there, the runtime configuration parameters must be set and then the Jetson cluster can be scaled and begin Federated Learning

### Environment Setup
The environment dependencies required to run the framework are:

 1. Docker
 2. Ansible
 3. Docker Python Client
 4. jsondiff

On all Jetpack systems, Docker is installed by default. The remaining dependencies can be install by running the following command from the root directory:

    python3 -m pip install -r requirements.txt

The requirements file will install the properly version dependencies within the Jetson environment.

Additionally, the BETH dataset must be present within the Jetson environment in order to train an initial model, and stream data to each training node in the cluster during Federated Learning. The dataset can be downloaded from the previously mentioned link. The dataset will be mounted as a volume in the appropriate Docker containers. This parameter is set within the Anisble inventory.yaml file.  

### Docker Environment Setup
A known limitation of Docker Swarm is how the service utilizes GPU resources on nodes in the Swarm cluster. Since ML processes are taking place during Federated Learning, it is expected that users would want to utilize a Jetson device's onboard GPU during said processes. In order to support this in a Swarm environment, the Nvidia runtime must be set by default in the Docker Daemon configuration file in /etc/docker/daemon.json. An example configuration is as follows:

    {
    "runtimes": {
        "nvidia": {
            "path": "nvidia-container-runtime",
            "runtimeArgs": []
          }
      },
      "default-runtime": "nvidia"
    }


The important parameter to make note of is "default-runtime". Having this set in the Docker Daemon configuration file will set all containers to use the Nvidia runtime by default, thus exposing the GPU to all running containers. For all nodes partaking in Federated Learning, it is recommended that this be set for optimal performance. 

### Setting Configuration Parameters
Before deploying the Federated Learning Environment with Ansible, a few runtime configuration parameters must be filled out. Within the configuration directory, the federated_learning and ansible directories both contain configuration information that must be filled out before deployment. 

In the Federated Learning directory a federated_learning.yaml file is present with comments explaining what each field represents for the Federated Learning Configuration

Similarly to Federated Learning, in the ansible directory, an inventory.yaml file is present where the host information and variables are to be filled out which correspond to the Jetson environment that the framework will be scaled to. 

### Creating the Cluster
Within the root directory, run the following command to create and scale out the Federated Learning Environment

    make all
This command will perform the following:

 1. Build the baseline model and scaler used during Federated Learning
 2. Create the Docker runtime environment
 3. Add each node to a Docker Swarm for node management
 4. Create a local repository to distribute the framework Docker image to each node in the cluster
 5. Deploy the Federated Learning Stack to the Swarm

From there, an MQTT listener such as MQTT Explorer can be used to view the messages being distributed from each node in the cluster. To view the progress of individual services in the cluster, Docker service logs can be viewed to track the progress of each service as they perform their tasks

### Scaling the Cluster
Since Docker Swarm is being used to manage the cluster of Jetson devices, the cluster can be scaled either up or down in nodes partaking in Federated Learning. Modify the inventory.yaml file in the Ansible configuration directory and add hosts to either the worker_train or worker_predict host groups to scale the cluster up. If scaling down, remove hosts from either group and add them to the decomissioned_workers host group. When the changes have been made, enter the following command to scale the cluster:

    make scale_swarm

### Rebuilding Base Model
In the event that the model/scaler used by the framework need to be recreated, the following command can be ran to achieve that. 

    make rebuild_model

### Redeploy with New Configuration Parameters 
If configuration parameters must be changed, a rolling update of all services in the Docker Swarm can be achieved by entering the following command:

    make update_fedLearn_configuration

### Destroy Swarm
When finished using the framework, the Docker Swarm can be scaled down and removed by entering the following command:

    make destroy_docker_swarm

When all services have been stopped, an updated model will be stored in the artifacts directory on the manager host of the Docker Swarm cluster. 
This model can be used for future iterations of Federated Learning or for an application that uses the model. 
