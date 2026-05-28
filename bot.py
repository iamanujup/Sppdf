import os
import re
import asyncio

asyncio.set_event_loop(asyncio.new_event_loop())

from pyrogram import Client, filters
from PyPDF2 import PdfReader, PdfWriter

# ==============================
# CONFIG
# ==============================

API_ID = int(os.getenv("API_ID", "5074166"))
API_HASH = os.getenv("API_HASH", "3cb93a9a9345592f5e6a42020687cdbe")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8809092646:AAEPX9hfULZ07jm8p10HxquHLKo7m22XuJw")

# ==============================
# APP
# ==============================

app = Client(
    "pdf_study_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ==============================
# FOLDERS
# ==============================

os.makedirs("downloads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

user_pdfs = {}

# ==============================
# START MESSAGE
# ==============================

START_TEXT = """
📚 PDF STUDY BOT

✨ Features:
✅ Extract PDF Pages
✅ PDF Information
✅ Text Extractor
✅ MCQ Extractor

📥 Send a PDF file to begin.
"""

# ==============================
# START COMMAND
# ==============================

@app.on_message(filters.command("start"))
async def start(_, message):
    await message.reply_text(START_TEXT)

# ==============================
# RECEIVE PDF
# ==============================

@app.on_message(filters.document)
async def receive_pdf(_, message):

    if message.document.mime_type != "application/pdf":
        await message.reply_text("❌ Please send PDF file only.")
        return

    msg = await message.reply_text("📥 Downloading PDF...")

    file_path = await message.download(
        file_name=f"downloads/{message.chat.id}.pdf"
    )

    user_pdfs[message.chat.id] = file_path

    try:
        reader = PdfReader(file_path)

        await msg.edit_text(
            f"""
✅ PDF Uploaded Successfully

📄 Total Pages: {len(reader.pages)}

📌 Commands:

🔹 /info
🔹 /text
🔹 /mcq
🔹 /extract 1-5
"""
        )

    except Exception as e:
        await msg.edit_text(f"❌ Error reading PDF\n\n{e}")

# ==============================
# PDF INFO
# ==============================

@app.on_message(filters.command("info"))
async def pdf_info(_, message):

    chat_id = message.chat.id

    if chat_id not in user_pdfs:
        await message.reply_text("❌ Upload PDF first.")
        return

    try:
        reader = PdfReader(user_pdfs[chat_id])

        await message.reply_text(
            f"""
📚 PDF INFO

📄 Total Pages: {len(reader.pages)}
🔒 Encrypted: {reader.is_encrypted}
"""
        )

    except Exception as e:
        await message.reply_text(f"❌ Error\n\n{e}")

# ==============================
# TEXT EXTRACTOR
# ==============================

@app.on_message(filters.command("text"))
async def extract_text(_, message):

    chat_id = message.chat.id

    if chat_id not in user_pdfs:
        await message.reply_text("❌ Upload PDF first.")
        return

    try:

        reader = PdfReader(user_pdfs[chat_id])

        text = ""

        for page in reader.pages[:5]:
            try:
                extracted = page.extract_text()

                if extracted:
                    text += extracted + "\n"

            except:
                pass

        if not text:
            text = "No readable text found."

        output = f"outputs/{chat_id}_text.txt"

        with open(output, "w", encoding="utf-8") as f:
            f.write(text[:40000])

        await message.reply_document(
            output,
            caption="✅ Text Extracted"
        )

        os.remove(output)

    except Exception as e:
        await message.reply_text(f"❌ Error\n\n{e}")

# ==============================
# MCQ EXTRACTOR
# ==============================

@app.on_message(filters.command("mcq"))
async def mcq_extractor(_, message):

    chat_id = message.chat.id

    if chat_id not in user_pdfs:
        await message.reply_text("❌ Upload PDF first.")
        return

    try:

        reader = PdfReader(user_pdfs[chat_id])

        text = ""

        for page in reader.pages[:10]:

            try:
                extracted = page.extract_text()

                if extracted:
                    text += extracted + "\n"

            except:
                pass

        lines = text.split("\n")

        mcqs = []

        for line in lines:

            if re.search(r"\b[A-D][\).]", line):
                mcqs.append(line)

        if not mcqs:
            mcqs = lines[:100]

        output = f"outputs/{chat_id}_mcq.txt"

        with open(output, "w", encoding="utf-8") as f:
            f.write("\n".join(mcqs[:200]))

        await message.reply_document(
            output,
            caption="✅ MCQ Extracted"
        )

        os.remove(output)

    except Exception as e:
        await message.reply_text(f"❌ Error\n\n{e}")

# ==============================
# PAGE EXTRACTOR
# ==============================

@app.on_message(filters.command("extract"))
async def extract_pages(_, message):

    chat_id = message.chat.id

    if chat_id not in user_pdfs:
        await message.reply_text("❌ Upload PDF first.")
        return

    try:

        args = message.text.split(" ")[1]

        start, end = map(int, args.split("-"))

        reader = PdfReader(user_pdfs[chat_id])

        total_pages = len(reader.pages)

        if start < 1 or end > total_pages:
            await message.reply_text("❌ Invalid page range.")
            return

        writer = PdfWriter()

        for i in range(start - 1, end):
            writer.add_page(reader.pages[i])

        output = f"outputs/{chat_id}_extract.pdf"

        with open(output, "wb") as f:
            writer.write(f)

        await message.reply_document(
            output,
            caption=f"✅ Extracted Pages {start}-{end}"
        )

        os.remove(output)

    except Exception as e:
        await message.reply_text(
            "❌ Usage:\n/extract 1-5"
        )

# ==============================
# RUN BOT
# ==============================

try:
    print("✅ PDF Study Bot Running...")
    app.run()

except Exception as e:
    print(f"❌ BOT ERROR:\n{e}")
