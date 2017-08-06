import os
import sys
import django
import paho.mqtt.client as mqttClient
from time import sleep

sys.path.insert(0, os.path.abspath(os.path.join(__file__ ,"../../..")))
os.environ["DJANGO_SETTINGS_MODULE"] = "servidor.settings"
django.setup()

from manutencao.log import log

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
        topico = msg.topic.split('/')
        # print(topico)
        packet = msg.payload.decode('utf-8')
        # print(packet)
        mensagem = eval(packet)
        # print(mensagem)
        if(topico[7] == 'sensor'):
            print('-------------NOVA LEITURA-------------')
            message = {
                'central': topico[2],
                'ambiente': topico[4],
                'grandeza': topico[6],
                'sensor': topico[8],
                'valor': mensagem['valor'],
                'createdAt': mensagem['createdAt']
            }
        if(topico[7] == 'alarme'):
            print('-------------ALARME-------------')
            message = {
                'central': topico[2],
                'ambiente': topico[4],
                'grandeza': topico[6],
                'codigoAlarme': topico[8],
                'uid': mensagem['uid'],
                'mensagem': mensagem['mensagem'],
                'prioridade': mensagem['prioridade'],
                'ativo': mensagem['ativo'],
                'tempoAtivacao': mensagem['tempoAtivacao'],
                'tempoInativacao': mensagem['tempoInativacao'] if mensagem['tempoInativacao'] else None
            }
        
        print(message)
    except Exception as e:
        print(e)

def onDisconnect(client, userdata, rc):
    log('MQTT', 'Conexão com o broker perdida')
    error = True
    while(error):
        try:
            client.reconnect()
            error = False
        except Exception as e:
            if(e.errno == 111):
                # print("Conexao recusada")
                pass
            else:
                print(dir(e))
                print(e)
            sleep(.01)
def conecta():
    nome = 'servidor' 
    
    client = mqttClient.Client(client_id=nome, clean_session=True, userdata="None", protocol="MQTTv311", transport="tcp")
    client.username_pw_set(username=nome)

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
