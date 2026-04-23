#!/usr/bin/env python3
"""
Gruppo 3 — Raspberry Pi Zero W Gateway
MQTT subscribe (robot/cmd) → Serial USB → Arduino Mega

Dipendenze:
    pip3 install paho-mqtt pyserial

Uso:
    python3 gateway.py
"""

import glob
import json
import time
import logging
import serial
import serial.serialutil
from paho.mqtt import client as mqtt

# ─────────────────────────────────────────────
# CONFIGURAZIONE — modifica questi valori
# ─────────────────────────────────────────────
BROKER_IP    = "localhost"   # IP del broker MQTT
BROKER_PORT  = 1883
MQTT_TOPIC   = "cmd"
MQTT_USER    = "robotuser"
MQTT_PWD     = "changeme"       # <-- sostituisci con la password reale
SERIAL_PORT  = "/dev/ttyACM0"  # oppure /dev/ttyUSB0
BAUD_RATE    = 9600

# Rate limiting: numero massimo di comandi al secondo
MAX_CMD_PER_SEC = 10
# ─────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
log = logging.getLogger("gateway")

# Mappatura comandi MQTT → lettera seriale
CMD_MAP = {
    "FORWARD":  "f",
    "BACKWARD": "b",
    "LEFT":     "l",
    "RIGHT":    "r",
    "STOP":     "s",
}

# Stato rate limiting
_last_cmd_times = []

ser: serial.Serial = None


def find_arduino_port() -> serial.Serial | None:
    """
    Cerca la prima porta ttyACM* o ttyUSB* disponibile.
    Prova prima SERIAL_PORT, poi scansiona le alternative.
    """
    candidates = [SERIAL_PORT] + sorted(
        glob.glob("/dev/ttyACM*") + glob.glob("/dev/ttyUSB*")
    )
    # Rimuovi duplicati mantenendo l'ordine
    seen = set()
    ordered = [p for p in candidates if not (p in seen or seen.add(p))]

    for port in ordered:
        try:
            s = serial.Serial(port, BAUD_RATE, timeout=1)
            if port != SERIAL_PORT:
                log.warning(f"Porta configurata non disponibile — uso {port} invece di {SERIAL_PORT}")
            log.info(f"Porta seriale aperta: {port} @ {BAUD_RATE} baud")
            return s
        except serial.serialutil.SerialException:
            continue
    return None


def open_serial() -> serial.Serial:
    """Apre la porta seriale verso Arduino. Riprova ogni 3 secondi se non disponibile."""
    while True:
        s = find_arduino_port()
        if s is not None:
            return s
        log.error("Nessuna porta Arduino trovata (cercato: ttyACM*, ttyUSB*). Riprovo tra 3 s...")
        time.sleep(3)


def is_rate_ok() -> bool:
    """Restituisce True se il comando rientra nel limite di frequenza."""
    global _last_cmd_times
    now = time.monotonic()
    # Tieni solo i timestamp nell'ultimo secondo
    _last_cmd_times = [t for t in _last_cmd_times if now - t < 1.0]
    if len(_last_cmd_times) >= MAX_CMD_PER_SEC:
        return False
    _last_cmd_times.append(now)
    return True


def build_serial_line(letter: str, speed: int, duration: int) -> str:
    """
    Costruisce la riga da inviare ad Arduino.
    Formato: LETTERA,velocità,durataMs\n
    Esempio: F,180,500\n  oppure  S,0,0\n
    """
    if letter == "S":
        return "S,0,0\n"
    speed    = max(0, min(255, speed))
    duration = max(0, duration)
    return f"{letter},{speed},{duration}\n"


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        log.info(f"Connesso al broker MQTT {BROKER_IP}:{BROKER_PORT}")
        client.subscribe(MQTT_TOPIC, qos=1)
        log.info(f"Sottoscritto a: {MQTT_TOPIC}")
    else:
        log.error(f"Connessione MQTT fallita, codice: {reason_code}")


def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
    log.warning(f"Disconnesso dal broker MQTT (codice: {reason_code}). Riconnessione automatica...")


def on_message(client, userdata, msg):
    global ser

    # ── Parsing JSON ──────────────────────────────
    try:
        data = json.loads(msg.payload.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        log.warning(f"Payload non valido: {e} → {msg.payload!r}")
        return

    cmd      = data.get("cmd", "").upper()
    speed    = int(data.get("speed", 0))
    duration = int(data.get("durationMs", 0))

    # ── Validazione comando ───────────────────────
    if cmd not in CMD_MAP:
        log.warning(f"Comando sconosciuto ignorato: '{cmd}'")
        return

    # ── Rate limiting ─────────────────────────────
    if not is_rate_ok():
        log.warning(f"Rate limit superato — comando '{cmd}' scartato")
        return

    # ── Costruzione riga seriale ──────────────────
    letter = CMD_MAP[cmd]
    line   = build_serial_line(letter, speed, duration)
    log.info(f"MQTT '{cmd}' → Seriale: {line.strip()}")

    # ── Invio su seriale ──────────────────────────
    if ser is None or not ser.is_open:
        log.error("Porta seriale chiusa — riapro...")
        ser = open_serial()

    try:
        ser.write(line.encode("ascii"))
    except serial.serialutil.SerialException as e:
        log.error(f"Errore scrittura seriale: {e} — riapro la porta")
        try:
            ser.close()
        except Exception:
            pass
        ser = open_serial()
        ser.write(line.encode("ascii"))


def main():
    global ser

    log.info("=== Gateway MQTT → Seriale avviato ===")

    # Apri seriale
    ser = open_serial()

    # Configura client MQTT
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect    = on_connect
    client.on_disconnect = on_disconnect
    client.on_message    = on_message

    # Reconnect automatico
    client.reconnect_delay_set(min_delay=1, max_delay=30)

    try:
        client.connect(BROKER_IP, BROKER_PORT, keepalive=60)
        client.loop_forever()
    except KeyboardInterrupt:
        log.info("Interruzione manuale — chiudo connessioni...")
    finally:
        client.disconnect()
        if ser and ser.is_open:
            ser.close()
        log.info("Gateway terminato.")


if __name__ == "__main__":
    main()
