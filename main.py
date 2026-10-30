import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai
from PIL import Image
import io

# الاعدادات
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash') # اسرع موديل

logging.basicConfig(level=logging.INFO)

# ذاكرة مؤقتة تحفظ نوع الماكينة لكل واحد
user_machines = {}

# برومبت ذكي يفهم كل ماكينات STOLL CMS
SYSTEM_PROMPT = """
انت خبير صيانة ماكينات STOLL CMS بكل انواعها (CMS 530, 330, 830, 933, 530 HP, ADF, etc).
المستخدم ماكينتو هي: {machine_type}

قواعد الرد:
1. رد بسرعة وبشكل مباشر، اعطي الحل فقط، لا تكثر اسئلة.
2. لا تقل "جرب كذا او كذا" - اعطي خطوة واحدة واضحة وسريعة.
3. تتكلم لهجة سورية بسيطة ومفهومة، يا معلم.
4. اذا سأل عن زيت، صوت، رسمة، برمجة، اعطيه الطريقة فورا.
5. اذا بعت صورة لقطعة او شاشة كمبيوتر او كيبورد، حلل الصورة وقلو شو المشكلة والحل فورا.
6. ما حدا بيستنى اكتر من 5 ثواني، لهيك ردك لازم يكون قصير وسريع ومفيد.
7. انت ذكاء اصطناعي متخصص فقط بماكينات STOLL CMS.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["CMS 530 HP", "CMS 330.6"], ["CMS 830", "CMS 933"], ["ADF 530-32", "ماكينتي نوع تاني"]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "أهلا يا معلم أسمر! 👋\n\nبشو بقدر ساعدك اليوم؟\n\n**أول شي قلي: شو نوع ماكينتك الـ STOLL؟**\nاحفظها مشان كلشي تسألني عنه جاوبك على أساسها.",
        reply_markup=markup
    )

async def save_machine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    
    # اذا اختار نوع ماكينة
    if "CMS" in text or "ADF" in text or "ماكينتي" in text:
        user_machines[user_id] = text
        await update.message.reply_text(f"تمام يا معلم! حفظت انو ماكينتك: **{text}** ✅\n\nهلأ اسألني اي شي: كيف زيتها، علي الصوت، نزل رسمة، او ابعتلي صورة للشاشة او للقطعة وانا فورا بعطيك الحل.")
        return

    # اذا سؤال عادي
    machine = user_machines.get(user_id, "غير محدد - اسألو اذا ما بيعرف")
    prompt = SYSTEM_PROMPT.format(machine_type=machine) + f"\n\nسؤال المستخدم: {text}\nردك السريع:"
    
    try:
        response = model.generate_content(prompt)
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text("لحظة يا معلم، عم حاول رد بسرعة... جرب تبعت سؤالك مرة تانية.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    machine = user_machines.get(user_id, "STOLL CMS عام")
    
    await update.message.reply_text("📸 شفت الصورة، عم حللها بسرعة...")

    photo_file = await update.message.photo[-1].get_file()
    photo_bytes = await photo_file.download_as_bytearray()
    image = Image.open(io.BytesIO(photo_bytes))

    prompt = SYSTEM_PROMPT.format(machine_type=machine) + "\n\nالمستخدم بعت صورة لقطعة او شاشة ماكينة STOLL. حلل الصورة واعطيه الحل المباشر والسريع. اذا فيها خطأ بالشاشة قلو شو هو وكيف يصلحو."

    try:
        response = model.generate_content([prompt, image])
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text("ما قدرت اقرا الصورة منيح يا معلم، ابعتها اوضح شوي او قلي شو مكتوب عالشاشة.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_machine))
    print("البوت السريع شغال...")
    app.run_polling()

if __name__ == "__main__":
    main()
