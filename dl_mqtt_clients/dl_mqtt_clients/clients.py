import abc
import paho.mqtt.client as mqtt
import ssl
import logging
from dl_mqtt_clients.func._general_func import _translate_mosq_protocol, _translate_ssl_protocol
from dl_mqtt_clients.configurations import MQTTConnectionConfig

class _mosq_client():

    def _validate_att(self):
        assert(isinstance(self.mqtt_config, MQTTConnectionConfig))
    
    def __init__(self, config, on_message_callb=None):
        """
        init just needs a configuration object of MQTTConnectionConfig
        optionally pass in a default callback function to execute on any topic that does not have a specific callback function
        otherwise, no default behavior specified
        """
        self.mqtt_config = config
        self._validate_att()
        self.client = mqtt.Client(client_id="",clean_session=True,userdata=None, 
                                    protocol=_translate_mosq_protocol(self.mqtt_config.mqtt_protocol()))
        self.client.on_connect = self._on_connect
        self.logger = logging.getLogger(self.__class__.__name__)
        self.topic_callback_map = {}
        if on_message_callb:
            self._set_default_callback(on_message_callb)
    
    def status(self):
        """
		Logs current topic subscriptions and callbacks associated
        """
        self.logger.info(self.topic_callback_map)

    def _on_connect(self, client, userdata, flags, rc):
        """
		Defines behavior for when client connects - the client will subscribe to the configured mqtt_config.sub_topics()
        """
        self.logger.info("Connected MQTT client. Result code {}".format(str(rc)))
        for t in self.mqtt_config.sub_topics():
            try:
                self.client.subscribe(topic=t, qos=self.mqtt_config.subQos())
                self.topic_callback_map[t] = 'default'
                self.logger.info('Subscribed to topic: {}'.format(t))
            except Exception as e:
                self.logger.error('Error with subscription to topic: {}'.format(t), exc_info=e)
                continue

    def _set_default_callback(self, on_message_callb):
        """
		Sets the default callback of the MQTT client
        """
        if self.client.on_message:
            self.logger.warning('default callback previously set. using _set_default_callback will overwrite. Overwriting ..')
        self.client.on_message = on_message_callb

    def connect_client(self):
        """
        Attempts to connect the client to the MQTT broker
        """
        if self.mqtt_config.ssl_cert_path():
            self.logger.info('SSL Auth. Enabled')
            self.client.tls_set(ca_certs=self.mqtt_config.ssl_cert_path(), tls_version=_translate_ssl_protocol(self.mqtt_config.sslProto()))

        self.logger.info('Attempting to connect to MQTT Broker ..')
        try:
            self.client.connect_async(self.mqtt_config.host(), self.mqtt_config.port(), self.mqtt_config.keepalive())
        except ConnectionRefusedError:
            self.logger.error("Error connecting to {}:{} ".format(self.mqtt_config.host(), self.mqtt_config.port()))
            raise
        self.client.loop_start()
    
    def add_callback(self, topic, callback):
        """
        adds a specific callback function for a certain topic
        """
        self.topic_callback_map[topic] = callback.__name__
        self.client.message_callback_add(topic, callback)
        
    def update_config(self, config):
        """
		Updates the MQTT Configuration object and reconnects the MQTT client

        args:
            config (dict): dictionary containing mqtt variable updates. Updates will be only made to valid keys
        """
        self.logger.info('Updating client config .. ')
        ret = self.mqtt_config.update_config(config)
        if ret:
            self.logger.info('Reconnecting MQTT client ..')
            try:
                self.client.reconnect()
            except Exception as e:
                self.logger.error('Error connecting MQTT client. Shutting down ...', exc_info=e)
                self.shutdown()
            self.logger.info('Configuration updates done.')
    
    def publish_msg(self, formatted_msg, pub_topic=None):
        """
		Publishes a formatted payload message to the broker.

        Args:
            formatted_msg (any): Message formatted to desire specification (e.g. str). Must be a readable type that is language-agnostic
            pub_topic (str) [Optional]: If specified, publish message to this topic. Otherwise publish to the objects configuration pub_topic 
        """
        _topic = pub_topic if pub_topic else self.mqtt_config.pub_topic()
        self.logger.debug("Out Msg - Len {}, Msg {}".format(len(formatted_msg), formatted_msg))
        self.logger.info("Publishing outgoing message to topic: {}".format(_topic))
        self.client.publish(topic=_topic, payload=formatted_msg, qos=self.mqtt_config.pubQos())

    def shutdown(self):
        """
		Stops the client loop and disconnects the client from the broker
        """
        self.logger.info('Client shutdown initiated')
        self.client.loop_stop()
        self.client.disconnect()
        self.logger.info('Client disconnected')