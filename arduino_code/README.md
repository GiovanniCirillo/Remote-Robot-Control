# Istruzioni d'Uso Progetto Arduino

## 🛠 Requisiti di Sistema
*   **Programma**: Arduino IDE

## 📥 Installazione
Per caricare il codice nella scheda tramite l'Arduino IDE, segui questi passaggi:

1.  **Selezione Scheda**: Vai su `Strumenti` > `Scheda` e seleziona il modello in uso (es. *Arduino Uno*).
2.  **Selezione Porta**: Vai su `Strumenti` > `Porta` e seleziona la porta COM corrispondente:
    *   **Windows**: `COM3` o superiore.
    *   **Mac/Linux**: `/dev/ttyACM` o simili.
3.  **Verifica (Opzionale)**: Clicca sul pulsante **Verifica** (icona del segno di spunta) per controllare eventuali errori di sintassi.
4.  **Caricamento**: Clicca sul pulsante **Carica** (icona della freccia) per compilare e trasferire il programma sulla scheda.

---

## 🕹 Comandi per Effettuare un Test
I comandi devono essere inviati tramite il **Monitor Seriale** dell'Arduino IDE.

### Esempio di comando:
`F, 255, 3000`

### Legenda Direzioni:

| Comando | Descrizione |
| :--- | :--- |
| **F** | Forward (Avanti) |
| **B** | Backward (Indietro) |
| **L** | Left (Sinistra) |
| **R** | Right (Destra) |

