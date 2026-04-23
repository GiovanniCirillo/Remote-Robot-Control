# Documentazione Progetto Gateway MQTT

## 📋 Requisiti di Sistema
* **Hardware**: Raspberry Pi
* **Sistema Operativo**: Raspberry Pi OS
* **Servizi**: 
    * Broker MQTT **Mosquitto**
    * Ambiente di esecuzione **Python**

---

## 🛠️ Installazione
1. **Trasferimento file**: Se utilizzi Windows, prepara il file e invialo al Raspberry tramite servizio **FTP**.
2. **Posizionamento**: Una volta trasferito, sposta il file all'interno di una cartella dedicata sul Raspberry Pi.

---

## ⚙️ Configurazione
Se Mosquitto non è installato localmente sullo stesso Raspberry:
* Apri il file di configurazione/script.
* Modifica la variabile `BROKER_IP`.
* Cambia `"localhost"` con l'**IP statico** del server Mosquitto.

---

## 🧪 Test di Funzionamento
Per eseguire il test, è consigliato aprire due sessioni terminale (es. tramite **Putty**).

### 1. Avvio del Gateway
Nel primo terminale, esegui lo script:
```bash
./gateway.py
```

### 2. Test di Ricezione
Nel secondo terminale, invia un messaggio semplice:
```bash
mosquitto_pub --host "BROKER_IP" --topic "topic" --message "ciao"
```
*Se funziona correttamente, vedrai apparire "ciao" nel primo terminale.*

### 3. Invio Comandi Robot
Per inviare istruzioni di movimento, usa la seguente sintassi:
```bash
mosquitto_pub -h "BROKER_IP" -u robotuser -P changeme \
  -t cmd -m '{"cmd":"FORWARD","speed":200,"durationMs":1000}'
```

**Dettagli parametri:**
* `cmd`: Direzione del movimento.
* `speed`: Velocità (valore consigliato: **200**).
* `durationMs`: Tempo di esecuzione del comando.
