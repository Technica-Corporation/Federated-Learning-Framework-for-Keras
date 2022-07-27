FROM nvcr.io/nvidia/l4t-tensorflow:r32.4.3-tf2.2-py3 AS base

#Upgrade pip and install dependencies
RUN python3 -m pip install -U pip
RUN python3 -m pip install scikit-learn==0.20.3 pyyaml==6.0 joblib==1.1.0 pandas==1.1.5

#Copy Codebase
COPY . /opt/FederatedLearning

FROM base AS final_build

#Install dl_mqtt_clients Python module and bake in pretrained model and scaler
WORKDIR /opt/FederatedLearning/dl_mqtt_clients
RUN python3 setup.py install
COPY artifacts /opt/FederatedLearning

FROM final_build AS config_redeploy 
COPY configuration/federated_learning /opt/FederatedLearning/configuration

