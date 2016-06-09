import logging
import paho.mqtt.client as paho
import json

import time
from kivy.app import App
from kivy.atlas import CoreImage
from kivy.properties import ListProperty, StringProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.core.image import Image
from kivy.uix.popup import Popup
from random import randint

log = logging.getLogger('client_metalink')
# presentation = Builder.load_file("mentalink.kv")

class GameOverPopup(Popup):
    pass

class Mentalink_Client(BoxLayout):
    image_handler = ObjectProperty()
    pass


class MentaLinkApp(App):
    timer = 0
    game_counter = StringProperty()
    player = 'user' + str(randint(0, 10000))
    status = ''
    mqttClient = paho.Client(player, False)
    currentGame = ''
    game_list = ListProperty([])

    def build(self):
        print(self.player)
        self.root = Mentalink_Client()

    def init_mqtt(self, broker='localhost'):
        # MQTT initialization
        self.mqttClient.on_connect = self.on_connect
        self.mqttClient.on_message = self.on_message
        self.mqttClient.connect(broker, 1883, 60)
        self.mqttClient.loop_start()
        self.mqttClient.publish('t_general', json.dumps({"type": "sign_in", "player": str(self.player)}))
        self.mqttClient.subscribe(str(self.player))

    def on_connect(self, client, userdata, flags, rc):
        print("MQTT connected with result code "+str(rc))
        self.mqttClient.subscribe("$SYS/#")

    def on_message(self, client, userdata, msg):
        if msg.topic == str(self.player):
            data = json.loads(msg.payload)
            if data["type"] == "game_list":
                self.game_list = data["games"]

        if msg.topic == str(self.currentGame + 'Q') or msg.topic == str(self.currentGame + '_on_join'):
            data = json.loads(msg.payload)
            if data['type'] == "image":
                print data['image']
                # self.root.ids.game_image.source = None
                self.root.ids.game_image.source = data['image']

                self.timer = 40
                while self.timer >= 0:
                    self.root.ids.timer.text = str(self.timer)
                    time.sleep(1)
                    self.timer -= 1
                if self.status == 'created':
                    self.mqttClient.publish(str(self.currentGame + '_control'), json.dumps({"type": "game_over"}))

            if data['type'] == "on_join":
                print data['image']
                # self.root.ids.game_image.source = None
                self.root.ids.game_image.source = data['image']
                while self.timer >= 0:
                    self.root.ids.timer.text = str(self.timer)
                    time.sleep(1)
                    self.timer -= 1

            if data['type'] == "score":
                print data['score_value']
                popup = GameOverPopup()
                popup.ids.score_label.text += str(data['score_value'])
                popup.open()
            # if data['type'] == "nr_players":
            #     self.nr_players = "Players: " + str(data['nr_players'])

            # if data['type'] == "counter":
            #     self.game_counter = "Game starting in " + str(data['value'])
            #     if data['value'] == 1:
            #         self.mqttClient.publish(str(self.currentGame + '_control'), json.dumps({"type": "start_game"}))
            #         # self.root.ids.screens.current = 'game_area'


    def send_ans(self, ans):
        self.mqttClient.publish(str(self.currentGame + 'A'), json.dumps({"ans": ans}))
        self.root.ids.answer_input.text = ''


    def on_stop(self):
        self.mqttClient.publish('t_general', json.dumps({"type": "sign_out", "player": self.player}))
        self.mqttClient.disconnect()
        self.mqttClient.loop_stop()

    def create_game(self, gameName):
        self.currentGame = gameName
        self.mqttClient.subscribe(str(gameName+'Q'))
        self.status = 'created'
        self.mqttClient.publish('t_general', json.dumps({"type": "new_game", "game": gameName, "author": self.player}))
        self.root.ids.screens.current = 'game_area'
        self.root.ids.game_name.text = 'GAME:  ' + gameName
        topic_game_control = str(gameName + '_control')
        time.sleep(1)
        self.mqttClient.publish(topic_game_control, json.dumps({"type": "start_game"}))

    def join_game(self, gameName):
        self.currentGame = gameName
        self.status = 'joined'
        self.root.ids.game_name.text = 'GAME: ' + gameName
        self.root.ids.screens.current = 'game_area'
        self.mqttClient.subscribe(str(gameName + 'Q'))
        self.mqttClient.subscribe(str(gameName + '_on_join'))
        time.sleep(1)
        self.mqttClient.publish(str(self.currentGame + '_control'), json.dumps({"type": "joined"}))
        # self.mqttClient.publish('t_general', json.dumps({"type": "connection", "joined": self.player}))


if __name__ == '__main__':
    mentalinkClient = MentaLinkApp()
    mentalinkClient.init_mqtt()
    mentalinkClient.run()
