import json
import paho.mqtt.client as mqtt
import pandas as pd
import time
import yaml
import numpy as np
from time import sleep
import logging

logging.basicConfig(level=logging.DEBUG)

def setup_mqtt_client(host, port, cert=None):
    client = mqtt.Client(client_id="", clean_session=True, userdata=None, protocol=mqtt.MQTTv311)
    if cert is not None:
        client.tls_set(cert, tls_version=ssl.PROTOCOL_TLSv1_2)
    client.connect(host, port, 60)

    return client

def cycle_datatype(generator_config, normal_data, current_cycle_time, l_start, l_end):
    current_cycle_time += (l_end - l_start)
    if(normal_data):
        if(current_cycle_time >= generator_config["n_time"]):
            normal_data = False
            current_cycle_time = 0
    else:
        if(current_cycle_time >= generator_config["a_time"]):
            normal_data = True
            current_cycle_time = 0

    return normal_data, current_cycle_time

def generator_loop(generator_config, client, normal_data):
    l_start = time.time()
    if(normal_data):
        df_mask = df[dataset_label] == 0
    else:
        df_mask = df[dataset_label] == 1

    # Get a single random row that is normal or anomalous
    df_sample = df[df_mask].sample(n=1, random_state=np.random.RandomState())
    df_sample = df_sample.drop(dataset_label, axis=1)
    json_sample = df_sample.to_json(orient="split", index=False)
    
    json_values = json.loads(json_sample)
    list_value = {"data": json_values["data"][0]}
       
    client.publish(generator_config["pub_topic"], str(list_value))
    if generator_config['publish_interval'] > 0:
        time.sleep(int(generator_config['publish_interval']))
    
    l_end = time.time()

    return l_start, l_end

def generate_data(generator_config):
    client = setup_mqtt_client(mqtt_host, mqtt_port)

    if generator_config["start_normal"]:
        normal_data = True
    else:
        normal_data = False

    current_cycle_time = 0
    t_end = time.time() + generator_config["total_runtime"]
    if generator_config["total_runtime"] > 0:
        while(time.time() <= t_end):
            l_start, l_end = generator_loop(generator_config, client, normal_data)
            if(generator_config["cycle_anomaly"]):
                normal_data, current_cycle_time = cycle_datatype(generator_config, normal_data, current_cycle_time, l_start, l_end)
    else:
        while(True):
            l_start, l_end = generator_loop(generator_config, client, normal_data)
            if(generator_config["cycle_anomaly"]):
                normal_data, current_cycle_time = cycle_datatype(generator_config, normal_data, current_cycle_time, l_start, l_end)
                
def process_data():
    """
    Prepare the dataset by completing the standard feature engineering tasks
    """
    
    df["processId"] = df["processId"].map(lambda x: 0 if x in [0, 1, 2] else 1)  # Map to OS/not OS
    df["parentProcessId"] = df["parentProcessId"].map(lambda x: 0 if x in [0, 1, 2] else 1)  # Map to OS/not OS
    df["userId"] = df["userId"].map(lambda x: 0 if x < 1000 else 1)  # Map to OS/not OS
    df["mountNamespace"] = df["mountNamespace"].map(lambda x: 0 if x == 4026531840 else 1)  # Map to mount access to mnt/ (all non-OS users) /elsewhere
#    df["eventId"] = df["eventId"]  # Keep eventId values (requires knowing max value)
    df["returnValue"] = df["returnValue"].map(lambda x: 0 if x == 0 else (1 if x > 0 else 2))  # Map to success/success with value/error
    

def main():
    global df, mqtt_host, mqtt_port, dataset_label
    generator_config = []
    
    with open("/opt/FederatedLearning/configuration/federated_learning/config.yaml", "r") as yamlfile:
        config = yaml.load(yamlfile, Loader=yaml.FullLoader)

    generator_config = config["data_generator"]
    mqtt_host = config["mqtt_connection"]["host"]
    mqtt_port = config["mqtt_connection"]["port"]
    features  = config["data_generator"]["features"]
    dataset_path = config["data_generator"]["dataset_path"]
    dataset_label = config["data_generator"]["dataset_label"]
    
    features.append(dataset_label)
    
    df = pd.read_csv(dataset_path) 
    df = df[features]
    process_data()
        
    generate_data(generator_config)

if __name__ == "__main__":
	main()


