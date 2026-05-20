import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ─── CONFIG ───────────────────────────────────────────────
VERIFY_TOKEN     = os.environ.get("VERIFY_TOKEN", "swiftmike_verify_2024")
ACCESS_TOKEN     = os.environ.get("ACCESS_TOKEN", "")
PHONE_NUMBER_ID  = os.environ.get("PHONE_NUMBER_ID", "105716248082993")
AGENT_NUMBER     = os.environ.get("AGENT_NUMBER", "")  # e.g. 2348107205278
API_URL          = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"

# ─── BOT RESPONSES ────────────────────────────────────────
WELCOME = """👋 Welcome to *SwiftMike Exchange!*
Your Swift Payment Route 💸

Reply with a number:

1️⃣ Check exchange rates
2️⃣ How to trade with us
3️⃣ Supported currencies
4️⃣ Transaction status
5️⃣ Fees & limits
6️⃣ Talk to an agent"""

RESPONSES = {
    "1": """💱 *Current Exchange Rates*

🇺🇸 USD → NGN: ₦1,570/dollar
🇬🇧 GBP → NGN: ₦1,980/pound  
🇪🇺 EUR → NGN: ₦1,690/euro
🇨🇦 CAD → NGN: ₦1,140/dollar
🇦🇺 AUD → NGN: ₦990/dollar
₿ USDT → NGN: ₦1,565/dollar

_Rates updated regularly. Contact us for bulk rates._

Reply *menu* to go back.""",

    "2": """📲 *How to Trade With Us*

1. Send us the amount you want to exchange
2. We give you our best rate
3. You send to our account/wallet
4. We pay you instantly ⚡

*We deal in:*
USD, GBP, EUR, CAD, AUD, NGN & Crypto (USDT, BTC, ETH)

WhatsApp us directly: 0810 720 5278

Reply *menu* to go back.""",

    "3": """🌍 *Supported Currencies*

We currently support:
• 🇺🇸 US Dollar (USD)
• 🇬🇧 British Pound (GBP)
• 🇪🇺 Euro (EUR)
• 🇨🇦 Canadian Dollar (CAD)
• 🇦🇺 Australian Dollar (AUD)
• 🇳🇬 Nigerian Naira (NGN)
• ₿ Crypto: USDT, BTC, ETH

*Global payments made simple, safe and swift.* ✅

Reply *menu* to go back.""",

    "4": """🔍 *Check Transaction Status*

To check your transaction, please provide:
• Your Transaction ID (e.g. SMX784521GHT)
• Or the amount & date of transfer

Send the details and an agent will confirm within *5 minutes* during business hours.

⏰ Business hours: Mon–Sat, 8am–9pm

Reply *menu* to go back.""",

    "5": """💰 *Fees & Limits*

✅ *No hidden fees* — what you see is what you get
✅ *Instant settlement* — paid in minutes, not days
✅ *Best rates* — competitive & transparent

*Minimum transaction:* $50 or equivalent
*Maximum:* No limit for verified clients

For bulk transactions, contact us directly for special rates.

Reply *menu* to go back.""",

    "6": "ESCALATE",
}

FALLBACK = """Sorry, I didn't understand that 😊

Please reply with a number (1–6) or type *menu* to see options again."""

ESCALATION = """🙋 Connecting you to a *live agent* now...

An agent will respond shortly.
⏰ Available: Mon–Sat, 8am–9pm

For urgent transactions, call/WhatsApp directly:
📞 *0810 720 5278*

Thank you for choosing *SwiftMike Exchange!* ✅"""

# ─── SEND MESSAGE ─────────────────────────────────────────
def send_message(to, text):
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    r = requests.post(API_URL, headers=headers, json=payload)
    print(f"Sent to {to}: {r.status_code} {r.text}")
    return r

def notify_agent(from_number, user_msg):
    if AGENT_NUMBER:
        msg = f"🚨 *Escalation Alert*\n\nCustomer {from_number} needs help.\nLast message: \"{user_msg}\"\n\nPlease respond."
        send_message(AGENT_NUMBER, msg)

# ─── BOT LOGIC ────────────────────────────────────────────
def get_reply(msg):
    msg = msg.strip().lower()
    if msg in ["hi", "hello", "hey", "start", "menu", "0"]:
        return WELCOME
    key = msg.replace(".", "").strip()
    response = RESPONSES.get(key)
    if not response:
        return FALLBACK
    return response

# ─── WEBHOOK ──────────────────────────────────────────────
@app.route("/webhook", methods=["GET"])
def verify():
    mode      = request.args.get("hub.mode")
    token     = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("Webhook verified!")
        return challenge, 200
    return "Forbidden", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        entry    = data["entry"][0]
        changes  = entry["changes"][0]
        value    = changes["value"]
        message  = value["messages"][0]
        from_num = message["from"]
        msg_body = message["text"]["body"]

        print(f"Message from {from_num}: {msg_body}")

        reply = get_reply(msg_body)

        if reply == "ESCALATE":
            send_message(from_num, ESCALATION)
            notify_agent(from_num, msg_body)
        else:
            send_message(from_num, reply)

    except (KeyError, IndexError) as e:
        print(f"Not a text message or parse error: {e}")

    return jsonify({"status": "ok"}), 200

# ─── RUN ──────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
