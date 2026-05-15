"""
Aggregatore Telegram - Filtra messaggi da canali pubblici e li manda ai tuoi Saved Messages
================================================================================
SETUP (una volta sola):
1. Vai su https://my.telegram.org → API development tools
2. Crea un'app, copia API_ID e API_HASH qui sotto
3. pip install telethon
4. Esegui lo script: python telegram_aggregatore.py
5. Al primo avvio chiede numero di telefono + codice OTP (come un login normale)
6. Dalla seconda volta in poi parte direttamente (sessione salvata in filtro_offerte.session)

COME FUNZIONA:
- Ascolta i canali in CANALI_SORGENTE in modalità push (si sveglia solo quando arriva qualcosa)
- Se il messaggio contiene almeno una parola chiave di KEYWORDS → lo forwarda a te
- "Hardware&offerte usato" è in CANALI_PASS_TUTTO → passa tutto senza filtro
- Nessun polling, nessun loop attivo: consuma risorse solo quando arriva un messaggio
"""

from telethon import TelegramClient, events

# ─── CONFIGURAZIONE ──────────────────────────────────────────────────────────

API_ID   = 36354931          # <-- inserisci il tuo API ID (numero intero)
API_HASH = "801c3e3a23a86e13e3eebd60bbc4b9e6"         # <-- inserisci il tuo API HASH (stringa)

# Canali da monitorare con filtro parole chiave
# Usa lo username del canale (quello dopo t.me/) oppure il link completo
CANALI_SORGENTE = [
    "CouponsItalia",          
    "offerteescontiTech",              
    "BestPrice_Errori_Offerte",              
    "couponsumarte",     
            
]
# Canale che passa tutto senza filtro (hardware usato: ti interessa quasi tutto)
CANALI_PASS_TUTTO = [
    "vereoffertewarehouse",     
]

# Parole chiave: se il messaggio contiene ALMENO UNA di queste → viene forwardato
# Aggiungile o toglile liberamente, non fa differenza maiuscolo/minuscolo
KEYWORDS = [
    # Storage
    "ssd", "nvme", "m.2", "hard disk", "hdd",
    # RAM
    "ram", "ddr3", "ddr4", "ddr5", "dimm", "sodimm",
    # CPU / schede madri
    "processore", "cpu", "intel", "amd", "ryzen", "core i",
    "scheda madre", "motherboard", "socket",
    # GPU
    "scheda video", "gpu", "nvidia", "radeon", "geforce", "gtx", "rtx", "rx ",
    # Monitor
    "monitor", "display", "schermo",
    # Alimentatori / case
    "alimentatore", "psu", "case pc",
    # Laptop ricondizionati
    "laptop", "notebook", "thinkpad", "latitude", "elitebook", "ricondizionato",
    # Altro hardware
    "raspberry", "switch", "router", "nas",
]

# Dove mandare i messaggi filtrati:
# "me" = i tuoi Saved Messages (la chat con te stesso, notifiche private)
# Oppure metti lo username di un tuo canale privato: "@mio_canale_privato"
DESTINAZIONE = "me"

# ─── SCRIPT ──────────────────────────────────────────────────────────────────

client = TelegramClient("filtro_offerte", API_ID, API_HASH)

tutti_i_canali = CANALI_SORGENTE + CANALI_PASS_TUTTO


def contiene_keyword(testo: str) -> bool:
    """Ritorna True se il testo contiene almeno una keyword."""
    testo_lower = testo.lower()
    return any(kw.lower() in testo_lower for kw in KEYWORDS)


@client.on(events.NewMessage(chats=tutti_i_canali))
async def gestore_messaggi(event):
    """Chiamato da Telegram ogni volta che arriva un nuovo messaggio nei canali monitorati."""

    testo = event.message.text or ""
    chat = await event.get_chat()
    nome_canale = getattr(chat, "username", None) or getattr(chat, "title", "sconosciuto")

    # Canali pass-tutto: forwarda senza controllare le keyword
    if nome_canale in CANALI_PASS_TUTTO or str(chat.id) in CANALI_PASS_TUTTO:
        await client.forward_messages(DESTINAZIONE, event.message)
        print(f"[PASS-TUTTO] {nome_canale}: forwarded")
        return

    # Canali filtrati: controlla le keyword
    if contiene_keyword(testo):
        await client.forward_messages(DESTINAZIONE, event.message)
        print(f"[MATCH] {nome_canale}: forwarded")
    else:
        print(f"[SKIP] {nome_canale}: nessuna keyword trovata")


print("Aggregatore avviato. In ascolto sui canali... (Ctrl+C per fermare)")
with client:
    client.run_until_disconnected()
