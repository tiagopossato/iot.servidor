cp jp.acl /etc/mosquitto/jp.acl
cp mosquitto.conf /etc/mosquitto/mosquitto.conf
cp mosquitto /etc/init.d/mosquitto
cp mosquitto.service /etc/systemd/system/mosquitto.service
systemctl enable mosquitto.service
