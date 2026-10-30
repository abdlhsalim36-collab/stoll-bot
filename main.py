import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
MY_ID = 1183273441

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash', system_instruction="انت خبير صيانة STOLL CMS 530 و CMS 330، ترد بالسوري المبسط، حلول عملية قصيرة.")

async def start(u,c):
    if u.effective_user.id != MY_ID: return
    kb=[[InlineKeyboardButton("CMS 530 HP 🔵",callback_data="530"),InlineKeyboardButton("CMS 330.6 ⚫️",callback_data="330")]]
    await u.message.reply_text("أهلاً يا معلم أسمر! البوت الجديد الروح شغال 🔥", reply_markup=InlineKeyboardMarkup(kb))

async def picked(u,c):
    try:
        q=u.callback_query; await q.answer(); await q.edit_message_text(f"✅ حفظت {q.data}")
    except: pass

async def chat(u,c):
    if u.effective_user.id != MY_ID: return
    ans = model.generate_content(u.message.text)
    await u.message.reply_text(ans.text)

app=ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start",start))
app.add_handler(CallbackQueryHandler(picked))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
app.run_polling()
