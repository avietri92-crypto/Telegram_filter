"""
Aggregatore Telegram - Versione Railway
Legge tutto da variabili d'ambiente, nessuna credenziale nel codice.
"""

import os
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

# ─── CREDENZIALI DA VARIABILI D'AMBIENTE ─────────────────────────────────────

API_ID         = os.environ.get("API_ID", "")
API_HASH       = os.environ.get("API_HASH", "")
SESSION_STRING = os.environ.get("SESSION_STRING", "")

# DEBUG
import sys
print(f"DEBUG API_ID: {'OK' if API_ID else 'MANCANTE'}")
print(f"DEBUG API_HASH: {'OK' if API_HASH else 'MANCANTE'}")
print(f"DEBUG SESSION_STRING: {'OK (len=' + str(len(SESSION_STRING)) + ')' if SESSION_STRING else 'MANCANTE'}")

if not API_ID or not API_HASH or not SESSION_STRING:
    print("ERRORE: variabili d'ambiente mancanti. Controlla Railway Variables.")
    sys.exit(1)

# ─── CONFIGURAZIONE CANALI ───────────────────────────────────────────────────

# Canali filtrati per parole chiave — metti gli username reali (dopo t.me/)
CANALI_SORGENTE = [
    "BestPrice_Errori_Offerte",
    "couponsumarte",
    "Couponsitalia",
    "offerteescontiTech",
]

# Canale pass-tutto (hardware usato: passa tutto senza filtro)
CANALI_PASS_TUTTO = [
    "vereoffertewarehouse",
]

BLACKLIST = [
    "Buona serata",
    "buongiorno",
    "buonanotte",
    "offerte del giorno",
    "segui i nostri canali",
]

# Parole chiave — modifica liberamente
KEYWORDS = [
    "ssd", "nvme", "m.2", "hard disk", "hdd",
    "ram", "ddr3", "ddr4", "ddr5", "dimm", "sodimm",
    "processore", "cpu", "intel", "amd", "ryzen", " core i ",
    "scheda madre", "motherboard", "socket",
    "scheda video", "gpu", "nvidia", "radeon", "geforce", "gtx", "rtx", "rx ",
    " monitor ", "display", "schermo",
    "alimentatore", "psu", "case pc",
    "laptop", "notebook", "thinkpad", "latitude", "elitebook", "ricondizionato",
    "raspberry", "switch", "router", " nas "," sega ",
]

# Destinazione: "me" = Saved Messages, oppure "@tuo_canale_privato"
DESTINAZIONE = "me"

# ─── SCRIPT ──────────────────────────────────────────────────────────────────

client = TelegramClient(StringSession(SESSION_STRING), int(API_ID), API_HASH)

tutti_i_canali = CANALI_SORGENTE + CANALI_PASS_TUTTO

def is_blacklistato(testo: str) -> bool:
    testo_lower= testo.lower()
    return any(b in testo_lower for b in BLACKLIST)

def contiene_keyword(testo: str) -> bool:
    testo_lower = testo.lower()
    return any(kw.lower() in testo_lower for kw in KEYWORDS)


@client.on(events.NewMessage(chats=tutti_i_canali))
async def gestore_messaggi(event):
    testo = event.message.text or ""
    chat = await event.get_chat()
    nome_canale = getattr(chat, "username", None) or getattr(chat, "title", "sconosciuto")

    if nome_canale in CANALI_PASS_TUTTO or str(chat.id) in CANALI_PASS_TUTTO:
        await client.forward_messages(DESTINAZIONE, event.message)
        print(f"[PASS-TUTTO] {nome_canale}: forwarded")
        return
        #comunicazione trovato oggetto della BLACKLIST.
    if is_blacklistato(testo):
        print(f"[BLACKLIST] {nome_canale}")
        #comunicazione trovato oggetto giusto.
    if contiene_keyword(testo):
        await client.forward_messages(DESTINAZIONE, event.message)
        print(f"[MATCH] {nome_canale}: forwarded")
    else:
        print(f"[SKIP] {nome_canale}: nessuna keyword trovata")


print("Aggregatore avviato. In ascolto sui canali... (Ctrl+C per fermare)")
async def pulisci_saved_messages():
    print(f"[PULIZIA] Cancello i messaggi salvati - {datetime.now()}")
    async for msg in client.iter_messages("me"):
        await client.delete_messages("me", msg.id)
    print("[PULIZIA] Completata")

scheduler = AsyncIOScheduler()
scheduler.add_job(pulisci_saved_messages, "cron", hour=5, minute=0)
scheduler.start()
with client:
    client.run_until_disconnected()
