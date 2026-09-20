import os
import telebot
from openai import OpenAI
from flask import Flask
from threading import Thread

# 1. Setup Environment Variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')
HF_TOKEN = os.environ.get('HF_TOKEN')

# 2. Initialize Clients
bot = telebot.TeleBot(BOT_TOKEN)
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN
)

# 3. Flask Server (To keep Render alive)
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# 4. Telegram Bot Logic
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Hello! I am your AI Assistant powered by DeepSeek via Hugging Face. Ask me anything!")

@bot.message_handler(func=lambda message: True)
def chat(message):
    try:
        # Show "typing..." status in Telegram
        bot.send_chat_action(message.chat.id, 'typing')

        # Call Hugging Face API
        chat_completion = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3", # Or the model version you prefer
            messages=[
                {"role": "user", "content": message.text}
            ],
            max_tokens=500
        )

        response_text = chat_completion.choices[0].message.content
        bot.reply_to(message, response_text)

    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, "I'm having trouble thinking right now. Please try again later.")

# 5. Run Both Flask and Bot
if __name__ == "__main__":
    # Start Flask in a separate thread
    t = Thread(target=run_flask)
    t.start()
    
    # Start Bot Polling
    print("Bot is starting...")
    bot.infinity_polling()
