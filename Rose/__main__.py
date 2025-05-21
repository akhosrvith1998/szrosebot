import asyncio
import importlib
import re
import uvloop
from pyrogram import filters, idle
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, ChatPermissions
from Rose.menu import *
from Rose import *
from Rose.plugins import ALL_MODULES
from Rose.utils import paginate_modules
from lang import get_command
from Rose.utils.lang import *
from Rose.utils.commands import *
from Rose.mongo.rulesdb import *
from Rose.utils.start import *
from Rose.mongo.usersdb import *
from Rose.mongo.restart import *
from Rose.mongo.chatsdb import *
from Rose.mongo.subsdb import Subscriptions
from Rose.mongo.warndb import Warns
from datetime import datetime, timedelta

loop = asyncio.get_event_loop()
flood = {}
START_COMMAND = get_command("START_COMMAND")
HELP_COMMAND = get_command("HELP_COMMAND")
HELPABLE = {}

# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬

async def subscription_required(func):
    async def wrapper(client, message: Message):
        chat_id = message.chat.id
        sub_data = Subscriptions.get_sub(chat_id)
        
        if sub_data and datetime.now() < sub_data["expiry"]:
            return await func(client, message)
        else:
            await message.reply("❌ این گروه اشتراک معتبر ندارد!")
    return wrapper

# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬

@app.on_message(filters.command("بن") & admin_filter)
@subscription_required
async def ban_user(client, message: Message):
    if not message.reply_to_message:
        return await message.reply("⚠️ لطفا به یک پیام کاربر ریپلای کنید!")
    user_id = message.reply_to_message.from_user.id
    try:
        await app.ban_chat_member(message.chat.id, user_id)
        await message.reply(f"✅ کاربر {user_id} بن شد!")
    except Exception as e:
        await message.reply(f"❌ خطا: {str(e)}")

@app.on_message(filters.command("سکوت") & admin_filter)
@subscription_required
async def mute_user(client, message: Message):
    if not message.reply_to_message:
        return await message.reply("⚠️ لطفا به یک پیام کاربر ریپلای کنید!")
    user_id = message.reply_to_message.from_user.id
    try:
        await app.restrict_chat_member(
            message.chat.id,
            user_id,
            ChatPermissions(can_send_messages=False)
        await message.reply(f"🔇 کاربر {user_id} سکوت شد!")
    except Exception as e:
        await message.reply(f"❌ خطا: {str(e)}")

@app.on_message(filters.command("اخطار") & admin_filter)
@subscription_required
async def warn_user(client, message: Message):
    if not message.reply_to_message:
        return await message.reply("⚠️ لطفا به یک پیام کاربر ریپلای کنید!")
    user_id = message.reply_to_message.from_user.id
    Warns.add_warn(user_id, message.chat.id)
    await message.reply(f"⚠️ به کاربر {user_id} اخطار داده شد!")

@app.on_message(filters.command("شارژ") & filters.user(OWNER_ID))
async def charge_group(client, message: Message):
    try:
        days = int(message.command[1])
        Subscriptions.update_sub(message.chat.id, days)
        await message.reply(f"♻️ اشتراک گروه برای {days} روز تمدید شد!")
    except (IndexError, ValueError):
        await message.reply("⚠️ فرمت دستور: /شارژ [تعداد روز]")

# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬

async def start_bot():
    global HELPABLE
    for module in ALL_MODULES:
        imported_module = importlib.import_module("Rose.plugins." + module)
        if hasattr(imported_module, "__MODULE__"):
            HELPABLE[module] = imported_module
    
    print("✅ ماژول‌ها با موفقیت بارگذاری شدند")
    await app.start()
    await idle()

if __name__ == "__main__":
    uvloop.install()
    loop.run_until_complete(start_bot())