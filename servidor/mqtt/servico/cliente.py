import os
import sys
import django
import paho.mqtt.client as mqttClient
from time import sleep
import uuid
from distutils.util import strtobool
import datetime

sys.path.insert(0, os.path.abspath(os.path.join(__file__ ,"../../..")))
os.environ["DJANGO_SETTINGS_MODULE"] = "servidor.settings"
django.setup()

from manutencao.log import log
from sentinela.models import Alarme, Leitura

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
                'central': uuid.UUID(topico[2]),
                'ambiente': uuid.UUID(topico[4]),
                'grandeza': int(topico[6]),
                'sensor': uuid.UUID(topico[8]),
                'valor': float(mensagem['valor']),
                'created_at': datetime.datetime.fromtimestamp(float(mensagem['createdAt']))
            }
            # print(message)
            leitura = Leitura(
                valor=message['valor'],
                ambiente=message['ambiente'],
                created_at=message['created_at'],
                grandeza_id=message['grandeza'],
                sensor=message['sensor'],
                central_id=message['central']
            )
            leitura.save()
            print(leitura)

        if(topico[7] == 'alarme'):
            print('-------------ALARME-------------')
            message = {
                'central': uuid.UUID(topico[2]),
                'ambiente': uuid.UUID(topico[4]),
                'grandeza': int(topico[6]),
                'codigoAlarme': uuid.UUID(topico[8]),
                'uid':uuid.UUID(mensagem['uid']),
                'mensagemAlarme': mensagem['mensagem'],
                'prioridadeAlarme': int(mensagem['prioridade']),
                'ativo': mensagem['ativo'],
                'tempoAtivacao': datetime.datetime.fromtimestamp(float(mensagem['tempoAtivacao'])),
                'tempoInativacao': datetime.datetime.fromtimestamp(float(mensagem['tempoInativacao'])) if mensagem['tempoInativacao'] else None
            }

            alarme = Alarme(uid=message['uid'],
                            codigoAlarme=message['codigoAlarme'],
                            mensagemAlarme=message['mensagemAlarme'],
                            prioridadeAlarme=message['prioridadeAlarme'],
                            ativo=message['ativo'],
                            tempoAtivacao=message['tempoAtivacao'],
                            tempoInativacao=message['tempoInativacao'],
                            ambiente=message['ambiente'],
                            grandeza_id=message['grandeza'],
                            central_id=message['central']
                            )
            alarme.save()
            print(alarme)
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
