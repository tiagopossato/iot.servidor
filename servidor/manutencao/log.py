"""
"""
import datetime
import time
import unicodedata
from manutencao.models import Log

"""
Salva um log na tabela de logs
"""
def log(_tipo, _mensagem):
    try:
        lg = Log(mensagem=str(_mensagem), tipo = str(_tipo))
        lg.save()
        print('['+ datetime.datetime.fromtimestamp(time.time()).strftime('%d-%m-%Y %H:%M:%S')
    + '] [' + _tipo + '] [' + _mensagem + ']')
    except Exception as e:
        salvaArquivo('LOG01',str(e))
        salvaArquivo(_tipo,_mensagem)

"""
Salva uma linha de log no arquivo .csv
"""
def salvaArquivo(_tipo, _mensagem):
    _mensagem = unicodedata.normalize('NFKD', _mensagem).encode('ascii', 'ignore').decode("utf-8")
    arquivo = open("logs.csv","+a")
    arquivo.write("[")
    arquivo.write(datetime.datetime.fromtimestamp(time.time()).strftime('%d-%m-%Y %H:%M:%S'))
    arquivo.write("] [")
    arquivo.write(_tipo)
    arquivo.write("] [")
    arquivo.write(_mensagem)
    arquivo.write("]\n")
    arquivo.close()
    print('['+ datetime.datetime.fromtimestamp(time.time()).strftime('%d-%m-%Y %H:%M:%S')
    + '] [' + _tipo + '] [' + _mensagem + ']')    