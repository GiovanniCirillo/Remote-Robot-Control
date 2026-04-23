Inserire qui come installare e configurare il servizio mosquitto

INSTALLAZIONE TEST MOSQUITTO:

1 Verifica servizio e test Mosquitto
Ti spiego come testare correttamente Mosquitto su Raspberry in modo strutturato (verifica
servizio → test locale → test rete).
Supponiamo tu abbia già installato:
sudo apt install mosquitto mosquitto-clients

2 Verifica che il servizio sia attivo
sudo systemctl status mosquitto
Deve risultare:
active (running)
Se non è attivo:
sudo systemctl enable --now mosquitto

3 Test base locale (loopback)
Questo è il test fondamentale.
Apri Terminale 1:
mosquitto_sub -h localhost -t test/topic
Apri Terminale 2:
mosquitto_pub -h localhost -t test/topic -m "ciao"
Se tutto funziona, nel primo terminale compare:
ciao
Broker funzionante
Porta 1883 attiva
Pub/Sub corretto
1

4 Test da un altro dispositivo in rete
Trova IP del Raspberry:
hostname -I
Supponiamo sia 192.168.1.50
Da un altro PC:
mosquitto_sub -h 192.168.1.50 -t test/topic
Poi:
mosquitto_pub -h 192.168.1.50 -t test/topic -m "rete ok"
Se ricevi il messaggio → broker accessibile in LAN.

5 Verifica porta 1883
Sul Raspberry:
sudo ss -tlnp | grep 1883
Devi vedere mosquitto in ascolto.

6 Test con QoS (per didattica)
Subscriber:
mosquitto_sub -h localhost -t test/qos -q 1
Publisher:
mosquitto_pub -h localhost -t test/qos -m "messaggio qos1" -q 1

7 Test persistente (retain)
mosquitto_pub -h localhost -t test/retain -m "persistente" -r
Poi:
mosquitto_sub -h localhost -t test/retain
Anche dopo riavvio subscriber il messaggio resta.
2
Problema Causa
Connection refused servizio non attivo
Timeout da rete firewall / bind localhost
Non riceve nulla topic diverso

8 Se vuoi vedere i log live
sudo journalctl -u mosquitto -f
Oppure:
sudo tail -f /var/log/mosquitto/mosquitto.log

9 Problemi comuni

10 Test completo per il tuo progetto
Per simulare la pipeline:
Terminale 1:
mosquitto_sub -h localhost -t cmd
Terminale 2:
mosquitto_pub -h localhost -t cmd -m ’{"move":"forward"}’
Così stai già testando lo scenario reale.
Se vuoi, nel prossimo messaggio ti preparo:

• un mini script Python subscriber pronto per il gateway

• oppure un test automatico che verifica broker + seriale insieme

FORMATTAZIONE RASPBERRY: 

 Setup minimale per il tuo progetto
Dopo formattazione:
sudo apt install mosquitto mosquitto-clients python3-pip python3-venv
Fine.
Se vuoi, posso prepararti:

• una checklist di inizializzazione da dare agli studenti

• oppure uno script automatico che prepara il Pi Zero W come gateway MQTT pronto all’uso
