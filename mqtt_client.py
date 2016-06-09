import logging
import paho.mqtt.client as paho

log = logging.getLogger('mqtt')


class MqttClient(object):
    def __init__(self, name, broker='localhost', port=1883):
        self.client = paho.Client(name, False)
        self.client.on_message = self.on_request
        self.external_handler = None

        log.debug('Connecting to broker %s:%s', broker, port)
        self.client.connect(broker, port=port)

    def set_external_handler(self, handler):
        self.external_handler = handler

    def on_request(self, client, userdata, msg):
        '''Invoked when a message is received on t_requests'''
        if self.external_handler:
            self.external_handler(client, userdata, msg)
        else:
            log.debug('MQTT IN %s %s', msg.topic, msg.payload)