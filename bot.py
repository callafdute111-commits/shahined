import asyncio
import time
import telebot
from telebot import types
from telethon import TelegramClient
from telethon.tl.functions.channels import CreateChannelRequest, InviteToChannelRequest, EditAdminRequest
from telethon.tl.functions.messages import ExportChatInviteRequest, SendMessageRequest
from telethon.tl.types import ChatAdminRights, InputPeerChannel
from telethon.network.connection.tcpabridged import ConnectionTcpAbridged
import os

# --------------------
# USERBOT
api_id = 33100094
api_hash = "3d53aefecc496d07c330278f6daac66b"
phone = "+989020952219"

userbot = TelegramClient(
    "userbot_session",
    api_id,
    api_hash,
    connection=ConnectionTcpAbridged,
    timeout=60
)

# --------------------
# BOT
BOT_TOKEN = "5947320664:AAGoLUfaCO28RkAzYOil3YBSNwPqtgIYnnE"
bot = telebot.TeleBot(BOT_TOKEN)

# --------------------
# نام کاربری واسطه‌ها بدون @
ADMIN_USERS = [
    "legend_yt3",
    "S_VEOSS"
]

# --------------------
# محدودیت ۱۵ دقیقه
user_last_request = {}
REQUEST_COOLDOWN = 900

# --------------------
# شمارنده گروه
COUNTER_FILE = "group_counter.txt"
if os.path.exists(COUNTER_FILE):
    with open(COUNTER_FILE) as f:
        GROUP_NUMBER = int(f.read())
else:
    GROUP_NUMBER = 0

def next_group_number():
    global GROUP_NUMBER
    GROUP_NUMBER += 1
    with open(COUNTER_FILE, "w") as f:
        f.write(str(GROUP_NUMBER))
    return GROUP_NUMBER

# --------------------
async def create_group_and_get_links(group_name):
    await userbot.start(phone=phone)

    # ساخت سوپرگروپ
    result = await userbot(CreateChannelRequest(
        title=group_name,
        about="گروه واسطه گری",
        megagroup=True
    ))
    chat = result.chats[0]

    # دعوت واسطه‌ها یکی یکی و فول ادمین
    for username in ADMIN_USERS:
        entity = await userbot.get_entity(username)  # بدون @
        await userbot(InviteToChannelRequest(channel=chat, users=[entity]))

        # منتظر می‌شویم که عضو شوند
        while True:
            participants = await userbot.get_participants(chat)
            if any(p.id == entity.id for p in participants):
                break
            await asyncio.sleep(1)

        # بعد فول ادمین می‌دهیم
        rights = ChatAdminRights(
            change_info=True,
            post_messages=True,
            edit_messages=True,
            delete_messages=True,
            ban_users=True,
            invite_users=True,
            pin_messages=True,
            add_admins=True,
            manage_call=True
        )
        await userbot(EditAdminRequest(
            channel=chat,
            user_id=entity,
            admin_rights=rights,
            rank="واسطه"
        ))

    # لینک یکبار مصرف خریدار و فروشنده
    buyer = await userbot(ExportChatInviteRequest(peer=chat, usage_limit=1))
    seller = await userbot(ExportChatInviteRequest(peer=chat, usage_limit=1))

    # ارسال پیام خوش‌آمد داخل گروه توسط ربات
    bot_entity = await userbot.get_me()
    input_chat = InputPeerChannel(chat.id, chat.access_hash)
    await userbot(SendMessageRequest(
        peer=input_chat,
        message=(
            "💠 سلام!\n"
            "گروه واسطه گری آماده شد.\n"
            "لطفا فقط با واسطه‌های معتبر معامله کنید."
        )
    ))

    return buyer.link, seller.link

def run_create(group_name):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(create_group_and_get_links(group_name))

# --------------------
@bot.message_handler(commands=["start"])
def start_handler(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(
        types.KeyboardButton("🤝 واسطه گری | خرید فروش و طاق"),
        types.KeyboardButton("🆘 پشتیبانی")
    )
    bot.send_message(
        message.chat.id,
        "💠 | سلام کاربر عزیز ؛\n\n"
        "- جهت ثبت درخواست واسطه گری خرید و فروش یا طاق ، از طریق دکمه های ربات اقدام کنید.\n\n"
        "ℹ️ | تمامی کارها توسط ربات و به صورت خودکار انجام می‌شود.\n"
        "ℹ️ | واسطه گری معامله شما به عهده واسطه های معتبر علی اسکای می‌باشد.",
        reply_markup=markup
    )

# --------------------
@bot.message_handler(func=lambda message: message.text == "🤝 واسطه گری | خرید فروش و طاق")
def trade(message):
    uid = message.from_user.id
    now = time.time()

    if uid in user_last_request and now - user_last_request[uid] < REQUEST_COOLDOWN:
        remaining = int((REQUEST_COOLDOWN - (now - user_last_request[uid])) / 60)
        bot.send_message(message.chat.id, f"⏳ هنوز {remaining} دقیقه از درخواست قبلی نگذشته است.")
        return

    # پیام اول
    bot.send_message(message.chat.id, "✅ درخواست شما ثبت شد، تا چند ثانیه دیگر لینک ارسال می‌شود...")
    time.sleep(5)

    # ساخت گروه و دریافت لینک یکبار مصرف
    num = next_group_number()
    group_name = f"واسطه گری علی اسکای | {num}"
    buyer_link, seller_link = run_create(group_name)
    user_last_request[uid] = now

    # ارسال لینک‌های یکبار مصرف فقط، دکمه‌ها سر جای خودشون
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(
        types.KeyboardButton("🤝 واسطه گری | خرید فروش و طاق"),
        types.KeyboardButton("🆘 پشتیبانی")
    )

    bot.send_message(
        message.chat.id,
        f"✅ گروه معامله شما ثبت شد.\n\n"
        f"🛅 لینک خریدار: {buyer_link}\n"
        f"🛅 لینک فروشنده: {seller_link}\n\n"
        f"⚠️ لینک‌ها یکبار مصرف هستند و فقط برای دو طرف معامله می‌باشند.",
        reply_markup=markup
    )

# --------------------
@bot.message_handler(func=lambda message: message.text == "🆘 پشتیبانی")
def support(message):
    bot.send_message(message.chat.id, "🆘 برای پشتیبانی به این آیدی مراجعه کنید: @SUPPORT_ID")

# --------------------
bot.infinity_polling()
