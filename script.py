import os
import sqlite3
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Database setup
DATABASE = 'premium_users.db'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS premium_users (
                            user_id INTEGER PRIMARY KEY,
                            expiration_time TEXT)''')
        conn.commit()

# Load premium users from the database
def load_premium_users():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, expiration_time FROM premium_users')
        rows = cursor.fetchall()
        for row in rows:
            user_id, expiration_time = row
            premium_users[user_id] = datetime.strptime(expiration_time, '%Y-%m-%d %H:%M:%S')

# Save a premium user to the database
def save_premium_user(user_id, expiration_time):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('REPLACE INTO premium_users (user_id, expiration_time) VALUES (?, ?)',
                       (user_id, expiration_time.strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()

# Remove a premium user from the database
def remove_premium_user(user_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM premium_users WHERE user_id = ?', (user_id,))
        conn.commit()

# Storage for user statuses and expiration times
premium_users = {}
user_requests = {}  # Storage for user-specific requests

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hi! Send me a .txt file containing phone numbers, and I will convert it to a .vcf file. Only premium users can use this feature.\n\nBUY? PM @maourafa\n\n join for information \ninfo - https://t.me/+6pFtWrMYQ145MWNl.')

def handle_file(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if not is_premium_user(user_id):
        update.message.reply_text('You need to be a premium user to use this feature.')
        return

    document = update.message.document
    caption = update.message.caption

    if caption:
        try:
            # Parse the caption
            filename, count_str = caption.split()
            count = int(count_str)

            # Download the file
            file = context.bot.get_file(document.file_id)
            file_path = file.download()

            # Process the file
            with open(file_path, 'r') as f:
                lines = f.readlines()

            # Split the lines into chunks
            chunks = [lines[i:i + count] for i in range(0, len(lines), count)]

            # Send the chunks back as separate files
            for i, chunk in enumerate(chunks):
                output_filename = f'{filename.split(".")[0]}_{i + 1}.txt'
                with open(output_filename, 'w') as out_file:
                    out_file.writelines(chunk)

                with open(output_filename, 'rb') as out_file:
                    context.bot.send_document(chat_id=update.message.chat_id, document=out_file)

            # Clean up
            os.remove(file_path)
            for i in range(len(chunks)):
                os.remove(f'{filename.split(".")[0]}_{i + 1}.txt')

        except ValueError:
            update.message.reply_text('Invalid format. Use: "filename.txt <number_of_contacts_per_file>"')
    else:
        update.message.reply_text('Please provide a caption with the format: "filename.txt <number_of_contacts_per_file>"')

def handle_document(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if not is_premium_user(user_id):
        update.message.reply_text('You need to be a premium user to use this feature.')
        return

    document = update.message.document
    file = context.bot.get_file(document.file_id)

    # Get original file name and replace with .vcf extension
    original_file_name = document.file_name
    vcf_file_name = original_file_name.replace('.txt', '.vcf')

    file_path = f'{document.file_id}.txt'
    file.download(file_path)

    # Process the file
    with open(file_path, 'r') as f:
        phone_numbers = f.readlines()

    # Remove the file after reading
    os.remove(file_path)

    vcf_content = create_vcf(phone_numbers)
    vcf_file_path = f'{document.file_id}.vcf'

    with open(vcf_file_path, 'w') as vcf_file:
        vcf_file.write(vcf_content)

    update.message.reply_document(document=open(vcf_file_path, 'rb'), filename=vcf_file_name)

    # Remove the generated .vcf file after sending
    os.remove(vcf_file_path)

def create_vcf(phone_numbers):
    vcf_entries = []
    for i, line in enumerate(phone_numbers, start=1):
        parts = line.strip().split('\t')
        phone_number = parts[0]
        contact_name = parts[1] if len(parts) > 1 else f'★魔王maou_CTC-{i:03d}'
        vcf_entry = (
            f"BEGIN:VCARD\n"
            f"VERSION:3.0\n"
            f"N:;{contact_name};;;\n"
            f"FN:{contact_name}\n"
            f"TEL;TYPE=CELL:{phone_number}\n"
            f"END:VCARD\n"
        )
        vcf_entries.append(vcf_entry)
    return "\n".join(vcf_entries)

def is_premium_user(user_id):
    if user_id in premium_users:
        expiration_time = premium_users[user_id]
        if expiration_time > datetime.now():
            return True
        else:
            remove_premium_user(user_id)  # Remove expired user
            del premium_users[user_id]
    return False

def set_premium(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id != ADMIN_USER_ID:
        update.message.reply_text('Only the admin can use this command.')
        return

    try:
        user_id = int(context.args[0])
        days = int(context.args[1])
        expiration_time = datetime.now() + timedelta(days=days)
        premium_users[user_id] = expiration_time
        save_premium_user(user_id, expiration_time)
        update.message.reply_text(f'User {user_id} is now a premium user for {days} days.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /setpremium <user_id> <days>')

def request_contact_split(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if not is_premium_user(user_id):
        update.message.reply_text('You need to be a premium user to use this feature.')
        return

    update.message.reply_text('Please send the number of contacts you want per file (example 100).')

    # Store the user's request state
    user_requests[user_id] = {"state": "awaiting_split_count"}

def split_vcard_file(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id not in user_requests or user_requests[user_id]["state"] != "awaiting_split_count":
        update.message.reply_text('Please use /requestsplit first to specify the number of contacts per file.')
        return

    try:
        contacts_per_file = int(update.message.text)
    except ValueError:
        update.message.reply_text('Invalid number. Please send a valid integer for the number of contacts per file.')
        return

    file_id = update.message.document.file_id
    file = context.bot.get_file(file_id)

    temp_folder = "temp"
    os.makedirs(temp_folder, exist_ok=True)
    temp_file_path = os.path.join(temp_folder, file.file_id + ".vcf")
    file.download(temp_file_path)

    with open(temp_file_path, 'r') as vcard_file:
        vcard_data = vcard_file.readlines()

    vcf_entries = []
    split_file_index = 1
    for line in vcard_data:
        vcf_entries.append(line)
        if line.strip() == 'END:VCARD':
            if len(vcf_entries) // 7 >= contacts_per_file:
                save_split_vcard(vcf_entries, split_file_index, update)
                split_file_index += 1
                vcf_entries = []

    if vcf_entries:
        save_split_vcard(vcf_entries, split_file_index, update)

    os.remove(temp_file_path)
    os.rmdir(temp_folder)

    del user_requests[user_id]

def save_split_vcard(vcf_entries, file_index, update):
    split_file_name = f"split_vcard_{file_index}.vcf"
    with open(split_file_name, 'w') as split_file:
        split_file.writelines(vcf_entries)
    update.message.reply_document(document=open(split_file_name, 'rb'), filename=split_file_name)
    os.remove(split_file_name)

def main() -> None:
    init_db()
    load_premium_users()

    # Replace 'YOUR_TOKEN' with your bot's API token
    updater = Updater("YOUR_TOKEN")

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("setpremium", set_premium))
    dispatcher.add_handler(CommandHandler("requestsplit", request_contact_split))  # Perintah untuk meminta jumlah kontak per file
    dispatcher.add_handler(MessageHandler(Filters.document.mime_type("text/plain") & Filters.caption, handle_file))
    dispatcher.add_handler(MessageHandler(Filters.document.mime_type("text/vcard"), split_vcard_file))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    # Replace with your admin user ID
    ADMIN_USER_ID = 5581268701
    main()