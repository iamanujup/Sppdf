import os
import re
from pyrogram import Client, filters
from PyPDF2 import PdfReader, PdfWriter

API_ID = int(os.getenv("5074166"))
API_HASH = os.getenv("3cb93a9a9345592f5e6a42020687cdbe")
BOT_TOKEN = os.getenv("8809092646:AAEPX9hfULZ07jm8p10HxquHLKo7m22XuJw")

app = Client(
    "pdf_study_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

user_pdfs = {}

os.makedirs("downloads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

START_TEXT = """
📚 PDF STUDY BOT

Features:
✅ Extract Pages
✅ PDF Info
✅ MCQ Extractor
✅ Text Extractor

Send a PDF file.
"""

@app.on_message(filters.command("start"))
async def start(_, message):
    await message.reply_text(START_TEXT)

@app.on_message(filters.document)
async def receive_pdf(_, message):

    if message.document.mime_type != "application/pdf":
        await message.reply_text("❌ Send PDF only")
        return

    msg = await message.reply_text("📥 Downloading PDF...")

    path = await message.download(
        file_name=f"downloads/{message.chat.id}.pdf"
    )

    user_pdfs[message.chat.id] = path

    reader = PdfReader(path)

    await msg.edit_text(
        f"""✅ PDF Uploaded

📄 Total Pages: {len(reader.pages)}

Commands:
🔹 /extract 1-5
🔹 /info
🔹 /text
🔹 /mcq
"""
    )

@app.on_message(filters.command("info"))
async def pdf_info(_, message):

    chat_id = message.chat.id

    if chat_id not in user_pdfs:
        await message.reply_text("❌ Upload PDF first")
        return

    reader = PdfReader(user_pdfs[chat_id])

    await message.reply_text(
        f"""📚 PDF INFO

Pages: {len(reader.pages)}
Encrypted: {reader.is_encrypted}
"""
    )

@app.on_message(filters.command("text"))
async def extract_text(_, message):

    chat_id = message.chat.id

    if chat_id not in user_pdfs:
        await message.reply_text("❌ Upload PDF first")
        return

    reader = PdfReader(user_pdfs[chat_id])

    text = ""

    for page in reader.pages[:5]:
        try:
            text += page.extract_text() + "\n"
        except:
            pass

    output = f"outputs/{chat_id}_text.txt"

    with open(output, "w", encoding="utf-8") as f:
        f.write(text[:40000])

    await message.reply_document(output)

    os.remove(output)

@app.on_message(filters.command("mcq"))
async def mcq_extractor(_, message):

    chat_id = message.chat.id

    if chat_id not in user_pdfs:
        await message.reply_text("❌ Upload PDF first")
        return

    reader = PdfReader(user_pdfs[chat_id])

    text = ""

    for page in reader.pages[:10]:
        try:
            text += page.extract_text() + "\n"
        except:
            pass

    lines = text.split("\n")

    mcqs = []

    for line in lines:
        if re.search(r"\b[A-D]\)", line):
            mcqs.append(line)

    if not mcqs:
        mcqs = lines[:50]

    output = f"outputs/{chat_id}_mcq.txt"

    with open(output, "w", encoding="utf-8") as f:
        f.write("\n".join(mcqs[:200]))

    await message.reply_document(
        output,
        caption="✅ MCQ Extracted"
    )

    os.remove(output)

@app.on_message(filters.command("extract"))
async def extract_pages(_, message):

    chat_id = message.chat.id

    if chat_id not in user_pdfs:
        await message.reply_text("❌ Upload PDF first")
        return

    try:

        args = message.text.split(" ")[1]

        start, end = map(int, args.split("-"))

        reader = PdfReader(user_pdfs[chat_id])

        writer = PdfWriter()

        for i in range(start - 1, end):
            writer.add_page(reader.pages[i])

        output = f"outputs/{chat_id}_extract.pdf"

        with open(output, "wb") as f:
            writer.write(f)

        await message.reply_document(
            output,
            caption=f"✅ Pages {start}-{end}"
        )

        os.remove(output)

    except Exception as e:
        await message.reply_text(f"❌ Error\n{e}")

print("✅ PDF Study Bot Running...")
app.run()
