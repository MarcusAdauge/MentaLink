import paho.mqtt.client as paho
import json
from collections import Counter

import time

from game_logic import Game


class GameServer:
    def __init__(self):
        self.running = True
        self.mqttClient = paho.Client('Server', False)
        self.games = []

    def init_mqtt(self, broker='localhost'):
        # MQTT initialization
        self.mqttClient.on_connect = self.on_connect
        self.mqttClient.on_message = self.on_message
        self.mqttClient.connect(broker, 1883, 60)
        self.mqttClient.loop_start()
        self.mqttClient.subscribe('t_general')

    def on_connect(self, client, userdata, flags, rc):
        print("MQTT connected with result code "+str(rc))
        self.mqttClient.subscribe("$SYS/#")

    def on_message(self, client, userdata, msg):
        if msg.topic == 't_general':
            data = json.loads(msg.payload)
            if data['type'] == "new_game":
                gameName = str(data['game'])
                print(gameName)
                try:
                    newGame = Game(len(self.games), gameName, data['author'])
                    self.games.append(newGame.gameName)
                    newGame.start()
                except:
                    print "Error: unable to start the thread for the new game"
            elif data['type'] == "sign_in":
                self.mqttClient.publish(str(data['player']), json.dumps({"type": "game_list", "games": self.games}))
            elif data['type'] == "sign_out":
                pass


if __name__ == '__main__':
    server = GameServer()
    server.init_mqtt()
    while server.running:
        pass

    print 'Server shouting down!'
    server.mqttClient.disconnect()
    server.mqttClient.loop_stop()
