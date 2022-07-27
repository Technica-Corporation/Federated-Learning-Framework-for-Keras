import sys, os
import logging
import argparse
import yaml
import signal

from datetime import datetime
from dl_mqtt_clients import configurations, KerasNN

logger = logging.getLogger(__name__)

class GracefulShutdown:
    def __init__(self, runtime, entrypoint):
        self.shutdown_now = False
        self.runtime = runtime
        self.entrypoint = entrypoint
        signal.signal(signal.SIGINT, self.handle_exit)
        signal.signal(signal.SIGTERM, self.handle_exit)
        signal.signal(signal.SIGHUP, self.handle_exit)

    def handle_exit(self, signum, frame):
        if self.runtime == "merge_model":
            logger.info("Saving latest model!")
            self.entrypoint.model.save_model("/opt/FederatedLearning/artifacts/updated_model")
        self.shutdown_now = True
    
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    
def parse_configurations(filename):
    logger.info("Parsing config from {}".format(filename))
    
    if not os.path.isfile(filename):
		    logger.error('(!) File config does not exist: {}'.format(filename))
		    sys.exit(1)

    with open(filename, 'r') as stream:
        try:
            config = yaml.load(stream, Loader=yaml.SafeLoader)
        except yaml.scanner.ScannerError as e:
            logger.error("error scanning configuration file. Exiting.. ({})".format(e))
            sys.exit(1)
    
    return config
 
def set_logging(function_type, log_path, debug):
    log_file_name = datetime.now().strftime(f'fedLearning_{function_type}_%d_%m_%Y')
    if debug:
        logging.basicConfig(format="%(asctime)s [%(name)-12.12s] [%(levelname)-6s]  %(message)s", level=logging.DEBUG,
												    handlers=[
													  logging.FileHandler("{0}/{1}.log".format(log_path, log_file_name)),
													  logging.StreamHandler()])
    else:
        logging.basicConfig(format="%(asctime)s [%(name)-12.12s] [%(levelname)-7s]  %(message)s", level=logging.INFO,
												    handlers=[
													  logging.FileHandler("{0}/{1}.log".format(log_path, log_file_name)),
													  logging.StreamHandler()])
                                                                                                                        
def set_mqtt_configuration(config_dict):
    if type(config_dict['predict_mqtt_topics']['sub_topics']) == str:
        config_dict['predict_mqtt_topics']['sub_topics'] = [str(s) for s in config_dict['predict_mqtt_topics']['sub_topics'].split(',')]
   
    logger.info('Loading data and validating configurations ..')
    
    config_dict['predict_mqtt_topics'].update(config_dict['mqtt_connection'])
    config_dict['training_mqtt_topics'].update(config_dict['mqtt_connection'])
    config_dict['manager_mqtt_topics'].update(config_dict['mqtt_connection'])
 
    try:
        predict_mqtt_c = configurations.MQTTConnectionConfig(c=config_dict['predict_mqtt_topics'])
   
    except AssertionError:
        config_errors = True

    try:
        training_mqtt_c = configurations.MQTTConnectionConfig(c=config_dict['training_mqtt_topics'])
   
    except AssertionError:
        config_errors = True

    try:
        manager_mqtt_c = configurations.MQTTConnectionConfig(c=config_dict['manager_mqtt_topics'])
   
    except AssertionError:
        config_errors = True
   
    return config_dict, predict_mqtt_c, training_mqtt_c, manager_mqtt_c
   
def set_entrypoint(function_type, config_dict, config_errors):
    config_dict, predict_mqtt_c, training_mqtt_c, manager_mqtt_c = set_mqtt_configuration(config_dict)  
    
    n = KerasNN()
    try:
        n.load_model(hdf5_filename=config_dict['nn_config']['model_path'])
    except KeyError:
        logger.error('KeyError: missing nn_config/model_path')
        config_errors=True
    
    if function_type == "train" or function_type == "predict":
        #Importing train/predict specific functionality
        from dl_mqtt_clients import ad_mosqeras
        from dl_mqtt_clients.func._nn_func import load_scaler
        from dl_mqtt_clients.payload_serializers.JSONSerializer import JSONSerializer
        
        s = JSONSerializer()
	      
        try:
	          scaler = load_scaler(h5_path=config_dict['nn_config']['scaler_path'])
        except KeyError:
            logger.error('KeyError: missing nn_config/scaler_path')
            config_errors=True
                    
        if function_type == "predict":
        
            #Set Entrypoint for predict
            logger.info("Starting the prediction Federated Learning Microservice")
            entrypoint = ad_mosqeras.predict_client(model = n, 
                                                    sk_scaler = scaler, 
                                                    mqtt_config = predict_mqtt_c, 
                                                    serializer = s,
                                                    model_update_topic = config_dict['nn_config']['model_update_topic'],
                                                    cache_sz = config_dict['predict_mqtt_topics']['cache_size'])
        
                                                                                                                                                                    
        elif function_type == "train":
            try:
                k_c = configurations.KerasConfig(c=config_dict['train'])
                k_c.output_config()
            except AssertionError:
                config_errors = True
                
            #Set Entrypoint for train 
            logger.info("Starting the training Federated Learning Microservice")             
       	    entrypoint = ad_mosqeras.train_client(model = n, 
								                                  sk_scaler = scaler, 
								                                  mqtt_config = training_mqtt_c,
							                                    serializer = s,
						                                      model_update_topic = config_dict['nn_config']['model_update_topic'],
								                                  cache_sz = config_dict['training_mqtt_topics']['cache_size'])
            entrypoint.set_train_config(k_c)   
               
    elif function_type == "merge_model":  
        #Importing merge_model specific functionality
        from dl_mqtt_clients import ModelAggregator      
        
        try:
            server_c = configurations.ModelServerConfig(c=config_dict['merge_model'])
            server_c.output_config()
        except AssertionError:
            config_errors = True
        serverStatusUpdateT = config_dict['status_update_pub_topic']
        logger.info('Server status update publish topic: {}'.format(serverStatusUpdateT))
        
        #Set Entrypoint for merge_model
        logger.info("Starting the merge model Federated Learning Microservice")
        entrypoint = ModelAggregator(model = n,
                                     mqtt_config=manager_mqtt_c, 
                                     server_config=server_c, 
                                     status_update_topic=serverStatusUpdateT)
             
    if config_errors:
        sys.exit(1)
    
    return entrypoint

sys.excepthook = handle_exception

def main():
    logger = logging.getLogger(__name__)
    cl_parser = argparse.ArgumentParser()
    cl_parser.add_argument("--config_path", "-cp", type=str, default="./ex_config_yaml/predict/config.yaml", help = "Path to config file")
    cl_parser.add_argument("--debug", action="store_true", default=False, help="Turns on debug logging level; otherwise INFO")
    cl_parser.add_argument("--log_path", default="./logs", help="Path to write log files")
    cl_parser.add_argument("--function_type", "-ft", type=str, default="predict", help="The type of entrypoint function. Can either be merge_model, train, predict")
    cl_args = cl_parser.parse_args()
    
  
    #Setting Variables for configuration and configuration validation 
    set_logging(cl_args.function_type, cl_args.log_path, cl_args.debug)
    config_dict = parse_configurations(cl_args.config_path)
    config_errors = False
    entrypoint = set_entrypoint(cl_args.function_type, config_dict, config_errors)
    
    #Setting SIGTERM handling for container shutdown
#    atexit.register(handle_exit, cl_args, entrypoint)
#    signal.signal(signal.SIGINT, handle_exit(cl_args, entrypoint))
    
    shutdown_handler = GracefulShutdown(cl_args.function_type, entrypoint)
    
    entrypoint.connect_clients()
    
    try:
        while not shutdown_handler.shutdown_now:
            pass
    except:
        entrypoint.shutdown()
        sys.exit(1)

if __name__=='__main__':
  main()
