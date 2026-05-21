import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

app = Flask(__name__)

# ─── CONFIG ───────────────────────────────────────────────
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN  = os.environ.get("TWILIO_AUTH_TOKEN", "")
TWILIO_NUMBER      = os.environ.get("TWILIO_NUMBER", "whatsapp:+14155238886")
AGENT_NUMBER       = os.environ.get("AGENT_NUMBER", "")

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

Reply *menu* to go back.""",

    "6": "ESCALATE",
}

FALLBACK = """Sorry, I didn't understand that 😊

Please reply with a number (1–6) or type *menu* to see options again."""

ESCALATION = """🙋 Connecting you to a *live agent* now...

An agent will respond shortly.
⏰ Available: Mon–Sat, 8am–9pm

For urgent transactions:
📞 *0810 720 5278*

Thank you for choosing *SwiftMike Exchange!* ✅"""

# ─── BOT LOGIC ────────────────────────────────────────────
def get_reply(msg):
    msg = msg.strip().lower()
    if msg in ["hi", "hello", "hey", "start", "menu", "0"]:
        return WELCOME
    key = msg.replace(".", "").strip()
    return RESPONSES.get(key, FALLBACK)

def notify_agent(from_number, user_msg):
    if AGENT_NUMBER and TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
        try:
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            client.messages.create(
                from_=TWILIO_NUMBER,
                to=f"whatsapp:{AGENT_NUMBER}",
                body=f"🚨 *Escalation Alert*\n\nCustomer {from_number} needs help.\nLast message: \"{user_msg}\"\n\nPlease respond."
            )
        except Exception as e:
            print(f"Agent notification error: {e}")

# ─── WEBHOOK ──────────────────────────────────────────────
@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "").strip()
    from_number  = request.values.get("From", "")

    print(f"Message from {from_number}: {incoming_msg}")

    resp = MessagingResponse()
    reply = get_reply(incoming_msg)

    if reply == "ESCALATE":
        resp.message(ESCALATION)
        notify_agent(from_number, incoming_msg)
    else:
        resp.message(reply)

    return str(resp)

@app.route("/", methods=["GET"])
def home():
    return "SwiftMike Bot is running! 🤖", 200

# ─── RUN ──────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
