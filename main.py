import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
PROFILE_FILE = "profile.json"

def load_profile():
    try:
        with open(PROFILE_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_profile(profile):
    with open(PROFILE_FILE, "w") as f:
        json.dump(profile, f, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hey. I'm your personal agent.\n\n"
        "Just talk to me normally. I'll remember things about you.\n"
        "Send /profile to see what I know."
    )

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    profile = load_profile()
    if not profile:
        await update.message.reply_text("I don't know anything about you yet. Tell me about yourself.")
        return
    text = "Here's what I know:\n\n"
    for key, value in profile.items():
        text += f"• {key}: {value}\n"
    await update.message.reply_text(text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    profile = load_profile()

    lower = user_text.lower()
    if "my name is" in lower or "i am" in lower or "i'm" in lower:
        profile["intro"] = user_text
    elif "i like" in lower or "i enjoy" in lower:
        profile["likes"] = user_text
    elif "skill" in lower or "i can" in lower or "i'm good at" in lower:
        profile["skills"] = user_text
    else:
        profile["last_message"] = user_text

    save_profile(profile)
    await update.message.reply_text("Noted. I'll remember that.")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Got your voice note. Transcription isn't set up in this free version yet, "
        "but I saved that you sent one. You can describe it in text for now."
    )

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_web():
    port = int(os.getenv("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    print(f"Health check server running on port {port}")
    server.serve_forever()

def main():
    # Start the health-check web server in a background thread
    threading.Thread(target=run_web, daemon=True).start()

    # Run the Telegram bot in the main thread
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
