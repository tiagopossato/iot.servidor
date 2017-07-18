import os
import sys
import django
import paho.mqtt.client as mqttClient
from collections import OrderedDict

sys.path.insert(0, os.path.abspath(os.path.join(__file__ ,"../..")))
os.environ["DJANGO_SETTINGS_MODULE"] = "servidor.settings"
django.setup()

from mqtt.models import User
from ecdsa import VerifyingKey, BadSignatureError

def onConnect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    if(rc==5):
        print("Invalid user or pass")
        #print(dir(client))
        client.disconnect()
        exit()
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("/central/#")

# The callback for when a PUBLISH message is received from the server.
def onMessage(client, userdata, msg):
    try:
        topico = msg.topic
        #usuario = msg.topic.split('/')[-1]
        packet = msg.payload.decode('utf-8')
#        print(topico + ": " + packet)
        message = eval(packet)
        print(message)
        #res, message = verificaAssinatura(usuario, packet)
        #if(res):
        #    print(message)

    except Exception as e:
        print(e)

def onDisconnect(client, userdata, rc):
    client.reconnect()
    #print("Até a próxima\n")
    #exit()


def verificaAssinatura(username, packet):
    u = User.objects.filter(username=username).get()
    pk = u.publickey
    vk = VerifyingKey.from_pem(pk)
    packet = eval(packet)
    message = packet['message']
    sig = packet['signature']
    try:
        vk.verify(sig, str(message).encode())
        print("Assinatura válida")
        return (True, message)
    except BadSignatureError:
        print("Assinatura inválida")
        return (False, None)


def conecta():
    u = User.objects.filter(username="servidor").get()
    nome = u.username
    senha = "servidor"
    
    client = mqttClient.Client(client_id=nome, clean_session=True, userdata="None", protocol="MQTTv311", transport="tcp")
    client.username_pw_set(username=nome, password=senha)

    client.on_connect = onConnect
    client.on_message = onMessage
    client.on_disconnect = onDisconnect

    client.connect("localhost", 1883, 60)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    try:
        client.loop_forever()
    except Exception as e:
        print(e)
    except KeyboardInterrupt as e:
        print("\nDesconectando...")
        client.disconnect()

conecta()
