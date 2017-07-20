import subprocess
from subprocess import CalledProcessError

SSL_DIR = "/etc/ssl/servidor/"

def criaCertificado(nomeCertificado, nomeCliente):
    try:
        subprocess.check_output([SSL_DIR+"/bin/create-client", "-n", str(nomeCertificado), "-c", str(nomeCliente)])
        return True
    except CalledProcessError as e:
        if(e.returncode == 1):
            print("Ja existe um certificado com este nome")    
            return False
        elif(e.returncode == 2):
            print("Argumentos incorretos: " + str(e.cmd))
            return False
        else:
            print()
            print(e.output.decode())
            print(e.returncode)
            return False
    pass

def revogaCertificado(nomeCertificado, razao=5):    
    try:
        subprocess.check_output([SSL_DIR+"/bin/revoke-cert", "-c", SSL_DIR+"certs/"+str(nomeCertificado)+".client.crt", "-r", str(razao)])
        return True
    except CalledProcessError as e:
        if(e.returncode == 1):
            print("Nao pode encontrar um certificado com este nome. " + str(e.output.decode()))    
            return False
        elif(e.returncode == 2):
            print("Argumentos incorretos: " + str(e.cmd))
            return False
        else:
            print()
            print(e.output.decode())
            print(e.returncode)
            return False
    pass

criaCertificado(nomeCertificado="teste4", nomeCliente="teste4")
