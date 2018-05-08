#!/bin/bash

#
# MAIN
#
if [ "$(id -u)" != "0" ]; then
	echo "Este script precisa ser executado com permissões de super-usuário (root)!"
	exit 1
fi

# Dependencias
#verifica a existencia da pasta da CA
if [ -d /etc/ssl/servidor ]; then
	echo "Crie a estrutura do CA antes de instalar o servidor"
	exit 1
fi

diretorio=$(pwd)

#instala as dependencias

apt install python3 python-pip python3-pip nginx supervisor sudo
pip install virtualenvwrapper

linha=("export WORKON_HOME=/opt/.envs")
cat /etc/profile | grep "$linha"
if [ $? -eq 1 ]; then
	echo $linha >> /etc/profile
fi

linha=("source /usr/local/bin/virtualenvwrapper.sh")
cat /etc/profile | grep "$linha"
if [ $? -eq 1 ]; then
	echo $linha >> /etc/profile
fi

source /etc/profile

mkvirtualenv servidorvenv --python=python3
workon servidorvenv

pip3 install -r requirements.txt

#cria usuario sem grupo e nem login
useradd -g www-data -M -r -s /usr/sbin/nologin servidor

echo
echo
echo
echo "Criar usuario para acesso remoto"
echo
echo
echo

#altera as permissoes do diretório da CA
chown servidor:www-data /etc/ssl/servidor -r

#verifica se já existe uma instalação
if [ -d /opt/iot.servidor ]; then
	#remove os arquivos do app existente
	if [ -d /opt/iot.servidor/servidor/ ]; then
		rm -r /opt/iot.servidor/servidor
	fi
else
	mkdir /opt/iot.servidor
fi

#verifica a existencia da pasta de log
if [ -d /opt/iot.servidor/log ]; then
	echo "A pasta de log de dados já existe, nada a fazer aqui"
else
	echo "Criando pasta de log"
	mkdir /opt/iot.servidor/log
fi


#Copia os novos arquivos
echo ".Copiando arquivos"
cp -r  ../servidor /opt/iot.servidor/

# Altera a variavel de DEBUG para False
sed -i '/DEBUG = True/c\DEBUG = False' /opt/iot.servidor/servidor/servidor/settings.py

echo "..Colentando arquivos estaticos"
python3 /opt/iot.servidor/servidor/manage.py collectstatic

echo "...Alterando permissoes"

# Tudo pertence ao usuario do servidor
chown servidor:nogroup /opt/iot.servidor -R
# Todos podem acessar o primeiro nivel de pastas
chmod 0755 /opt/iot.servidor

# Somente root e o usuario da central podem acessar a pasta e subpastas
chmod 0700 /opt/iot.servidor/servidor -R

# Os usuarios do grupo www-data também podem escrever na pasta de log
chown servidor:www-data /opt/iot.servidor/log -R
# Todos os usuarios podem visualizar os arquivos de log
chmod 0775 /opt/iot.servidor/log -R
# Somente o usuario www-data pode acessar a pasta de arquivos estaticos
chown www-data:www-data /var/www/static

#cp receptor.conf /etc/supervisor/conf.d/receptor.conf
cp servidor.conf /etc/supervisor/conf.d/servidor.conf

supervisorctl reload

echo "servidor ALL=(ALL) NOPASSWD: /bin/systemctl stop mosquitto, /bin/systemctl start mosquitto" > /etc/sudoers.d/servidor

echo "....Configurando nginx para servir os arquivos estaticos"
cp servidor_nginx.conf /etc/nginx/sites-available
rm /etc/nginx/sites-enabled/default
ln -s /etc/nginx/sites-available/servidor_nginx.conf /etc/nginx/sites-enabled/
systemctl restart nginx
