from collections import Counter
from threading import Thread
import paho.mqtt.client as paho
import json
import time
from random import randint

class Game(Thread):
    def __init__(self, threadID, name, author, mqttBroker = 'localhost'):
        Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.gameName = name
        self.players = [author]
        self.game_ans = []
        self.score = 0
        self.curImg = None
        self.mqttClient = paho.Client(name, False)
        self.mqttClient.on_connect = self.on_connect
        self.mqttClient.on_message = self.on_message
        self.mqttClient.connect(mqttBroker, 1883, 60)
        self.mqttClient.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        print("MQTT connected with result code "+str(rc))
        self.mqttClient.subscribe("$SYS/#")
        self.mqttClient.subscribe(str(self.gameName + '_control'))
        self.mqttClient.subscribe(str(self.gameName + 'A'))

    def on_message(self, client, userdata, msg):
        if msg.topic == str(self.gameName + '_control'):
            data = json.loads(msg.payload)
            # if data['type'] == "connection":
            #     self.players.append(data['joined'])
            #     self.mqttClient.publish(str(self.gameName + 'Q'), json.dumps({"type": "nr_players", "nr_players": len(self.players)}))
            if data['type'] == "start_game":
                self.curImg = "imgs/img"+str(randint(1,6))+".jpg"
                self.mqttClient.publish(str(self.gameName + 'Q'), json.dumps({"type": "image", "image": str(self.curImg)}))
            if data['type'] == "joined":
                self.mqttClient.publish(str(self.gameName + '_on_join'), json.dumps({"type": "on_join", "image": str(self.curImg)}))
            if data['type'] == "game_over":
                matches = dict(Counter(self.game_ans))
                print  matches
                for key, value in matches.iteritems():
                    self.score += (value * 10 - 10)
                self.mqttClient.publish(str(self.gameName + 'Q'), json.dumps({"type": "score", "score_value": self.score}))
                self.game_ans = []
                self.score = 0

        elif msg.topic == str(self.gameName + 'A'):
            data = json.loads(msg.payload)
            self.game_ans.append(data['ans'])
            print self.game_ans

    def run(self):
        counter = 10
        while counter >= 5:
            self.mqttClient.publish(str(self.gameName + 'Q'), json.dumps({"type": "counter", "value": counter}))
            time.sleep(1)
            counter -= 1
        print "Starting new game: " + self.name
        while True:
            pass
        print "Exiting the game: " + self.name
        self.mqttClient.disconnect()
        self.mqttClient.loop_stop()
