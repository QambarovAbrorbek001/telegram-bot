"""
Telegram Anonim Xabarlar Boti
Foydalanuvchilar shaxsiy link orqali anonim xabar yuborishlari mumkin.
aiogram 3.x asosida qurilgan.
"""

import logging
from datetime import datetime
from zoneinfo import ZoneInfo
import secrets
from typing import Optional

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import BaseMiddleware
import asyncio

from config import (
    TELEGRAM_BOT_TOKEN,
    RATE_LIMIT_MESSAGES,
    RATE_LIMIT_SECONDS,
    ADMIN_IDS,
    MAX_MESSAGE_LENGTH,
)
from database import DatabaseManager

# ============================================================
# Logging sozlamasi
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ============================================================
# Bot va dispatcher
# ============================================================
db  = DatabaseManager()
bot = Bot(token=TELEGRAM_BOT_TOKEN)   # ✅ Token faqat config orqali keladi
dp  = Dispatcher()

# ============================================================
# Subscription middleware — blocks non-subscribed users
# ============================================================
class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        # Determine user_id from event
        user_id = None
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
        else:
            return await handler(event, data)

        # Admins bypass
        if is_admin(user_id):
            return await handler(event, data)

        # Allow subscription check callback unconditionally
        if isinstance(event, CallbackQuery) and event.data == "subscription_check":
            return await handler(event, data)

        # Check subscription
        try:
            is_subscribed = await check_user_subscription(user_id)
        except Exception:
            is_subscribed = False

        if is_subscribed:
            return await handler(event, data)

        # Non-subscribed: block and show subscription screen
        if isinstance(event, Message):
            await event.answer(
                "📢 <b>Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling:</b>",
                parse_mode="HTML",
                reply_markup=subscription_required_keyboard()
            )
        elif isinstance(event, CallbackQuery):
            await event.answer("❌ Obuna talab qilinadi", show_alert=True)
        return

dp.message.middleware(SubscriptionMiddleware())
dp.callback_query.middleware(SubscriptionMiddleware())

# Vaqtinchalik xotira: sender_id -> recipient_id
pending_anonymous_targets: dict[int, int] = {}

# Reply-tugma matnlari (boshqa handlerlardan ajratib olish uchun)
CONTROL_BUTTON_LABELS = {"🔗 Mening linkim", "🏠 Bosh menyu", "❌ Bekor qilish"}

# ============================================================
# FSM holatlari
# ============================================================
class MessageStates(StatesGroup):
    waiting_for_message = State()
    waiting_for_reply = State()  # Reply mode active

class AdminStates(StatesGroup):
    broadcast_text = State()
    adding_channel = State()
    waiting_channel_invite = State()

# ============================================================
# Yordamchi funksiyalar
# ============================================================
async def get_personal_link(user_id: int) -> str:
    bot_info = await bot.get_me()
    token = db.create_or_get_user_token(user_id)
    return f"https://t.me/{bot_info.username}?start={token}"

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

def now_uz() -> str:
    return datetime.now(ZoneInfo("Asia/Tashkent")).strftime("%Y-%m-%d %H:%M:%S")

async def check_user_subscription(user_id: int) -> bool:
    """Check if user is subscribed to all required channels.
    Returns True if no channels required or user is member/has pending join request."""
    required = db.get_required_channels()
    if not required:
        return True
    for ch in required:
        try:
            # Determine chat identifier: prefer numeric ID, fallback to username
            chat_id = ch['channel_id']
            if chat_id == 0 and ch.get('channel_username'):
                chat_identifier = f"@{ch['channel_username']}"
            elif chat_id:
                chat_identifier = chat_id
            else:
                continue

            member = await bot.get_chat_member(chat_id=chat_identifier, user_id=user_id)
            status = member.status
            if status in ("member", "administrator", "creator", "restricted"):
                continue
            # If not member, fall through to pending check
        except Exception:
            # Not a member or cannot check — fall through to pending check
            pass

        # Check pending join request (only if we have numeric channel_id)
        if ch.get('channel_id') and db.has_pending_join_request(user_id, ch['channel_id']):
            continue
        return False
    return True

def subscription_required_keyboard() -> Optional[InlineKeyboardMarkup]:
    """Generate keyboard with required channel buttons; None if no channels"""
    channels = db.get_required_channels()
    if not channels:
        return None
    rows = []
    for ch in channels:
        if ch.get('channel_username'):
            username = ch['channel_username']
            url = f"https://t.me/{username}"
            text = f"📢 @{username}"
            rows.append([InlineKeyboardButton(text=text, url=url)])
        elif ch.get('invite_link'):
            url = ch['invite_link']
            text = "📢 Kanalga qo'shilish"
            rows.append([InlineKeyboardButton(text=text, url=url)])
        # If neither, skip (cannot create button)
    rows.append([InlineKeyboardButton(text="✅ Tekshirish", callback_data="subscription_check")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

# ============================================================
# Subscription check callback
# ============================================================
@dp.callback_query(F.data == "subscription_check")
async def cb_subscription_check(callback: types.CallbackQuery) -> None:
    if await check_user_subscription(callback.from_user.id):
        await callback.message.edit_text("✅ Obuna tasdiqlandi! Endi botdan foydalanishingiz mumkin.")
        await callback.answer("✅ Muvaffaqiyatli", show_alert=True)
        # Send main menu
        await callback.message.answer("📋 <b>Bosh menyu</b>", parse_mode="HTML", reply_markup=main_menu_keyboard())
    else:
        await callback.answer("❌ Hali obuna bo'lmagansiz. Barcha kanallarga obuna bo'ling va qaytadan tekshiring.", show_alert=True)

# ============================================================
# Klaviaturalar
# ============================================================
def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📬 Mening linkim",    callback_data="menu_get_link")],
        [InlineKeyboardButton(text="💬 Xabarlarim",       callback_data="menu_view_messages")],
        [InlineKeyboardButton(text="👤 Profilim",         callback_data="menu_profile")],
        [InlineKeyboardButton(text="❓ Yordam",           callback_data="menu_help")],
    ])

def reply_keyboard() -> types.ReplyKeyboardMarkup:
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="🔗 Mening linkim")],
            [types.KeyboardButton(text="🏠 Bosh menyu")],
            [types.KeyboardButton(text="❌ Bekor qilish")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
    )

def admin_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Foydalanuvchilar soni", callback_data="admin_user_count")],
        [InlineKeyboardButton(text="📢 Hammaga xabar yuborish", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="➕ Kanal ulash",           callback_data="admin_add_channel")],
        [InlineKeyboardButton(text="🗑 Kanalni o'chirish",    callback_data="admin_remove_channel")],
        [InlineKeyboardButton(text="🔄 Asosiy menyuga",       callback_data="menu_main")],
    ])

def message_actions_markup(message_id: int, sender_id: Optional[int] = None) -> Optional[InlineKeyboardMarkup]:
    """Inline keyboard for received anonymous messages — only reply (if sender known)"""
    if sender_id is None:
        return None
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↩️ Javob berish", callback_data=f"reply_start_{message_id}")]
    ])

# ============================================================
# Chat join request handler — records pending join requests
# ============================================================
@dp.chat_join_request()
async def handle_chat_join_request(chat_join_request: types.ChatJoinRequest) -> None:
    user_id = chat_join_request.from_user.id
    channel_id = chat_join_request.chat.id
    # Only record if this channel is in required_channels
    required_ids = db.get_all_required_channel_ids()
    if channel_id in required_ids:
        db.add_join_request(user_id, channel_id)
        logger.info(f"User {user_id} join request to required channel {channel_id} recorded")

# ============================================================
# /start
# ============================================================
# /start
# ============================================================
@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext) -> None:
    user_id    = message.from_user.id
    username   = message.from_user.username
    first_name = message.from_user.first_name
    last_name  = message.from_user.last_name

    db.register_user(user_id, username, first_name, last_name)
    logger.info(f"Foydalanuvchi {user_id} botni ishga tushirdi")

    args = message.text.split()
    if len(args) > 1:
        token = args[1]
        recipient_id = db.get_user_id_by_token(token)

        if not recipient_id:
            await message.answer(
                "❌ Noto'g'ri yoki eskirgan link.",
                reply_markup=main_menu_keyboard(),
            )
            return

        if recipient_id == user_id:
            await message.answer(
                "😅 O'zingizga anonim xabar yubora olmaysiz!",
                reply_markup=main_menu_keyboard(),
            )
            return

        pending_anonymous_targets[user_id] = recipient_id
        await state.set_state(MessageStates.waiting_for_message)
        recipient = db.get_user(recipient_id)
        recipient_name = recipient.get("first_name") or recipient.get("username") or f"Foydalanuvchi {recipient_id}"

        await message.answer(
            f"✍️ <b>{recipient_name}</b> ga anonim xabar yozmoqdasiz.\n\n"
            f"Xabaringizni yozing (maksimal {MAX_MESSAGE_LENGTH} belgi).\n"
            f"📝Hozirda botda faqat matnlar orqali habar yuborish mumkin.\n\n"
            f"Bekor qilish uchun <b>❌ Bekor qilish</b> tugmasni bosing.",
            parse_mode="HTML",
            reply_markup=reply_keyboard(),
        )
        return

    # Oddiy /start — bosh menyu
    link = await get_personal_link(user_id)
    welcome = (
        f"👋 <b>Anonim Xabarlar Botiga xush kelibsiz!</b>\n\n"
        f"🔗 Sizning shaxsiy linkingiz:\n"
        f"<code>{link}</code>\n\n"
        f"Bu linkni do'stlaringizga yuboring — ular sizga anonim xabar yubora olishadi!\n\n"
        f"Quyidagi menyudan foydalaning 👇"
    )
    await message.answer(welcome, parse_mode="HTML", reply_markup=reply_keyboard())
    await message.answer("📋 <b>Bosh menyu</b>", parse_mode="HTML", reply_markup=main_menu_keyboard())
    await state.clear()

# ============================================================
# /help
# ============================================================
@dp.message(Command("help"))
async def cmd_help(message: types.Message) -> None:
    text = (
        "🤖 <b>Anonim Xabarlar Boti — Yordam</b>\n\n"
        "<b>Buyruqlar:</b>\n"
        "/start — Botni ishga tushirish\n"
        "/help  — Yordam\n"
        "/menu  — Bosh menyu\n"
        "/profile — Profilingiz\n"
        "/messages — Qabul qilingan xabarlar\n"
        "/cancel — Joriy amalni bekor qilish\n\n"
        "<b>Qanday ishlaydi?</b>\n"
        "1️⃣ /start buyrug'ini yuboring\n"
        "2️⃣ Shaxsiy linkingizni oling\n"
        "3️⃣ Linkni do'stlaringizga yuboring\n"
        "4️⃣ Ular sizga anonim xabar yuborishadi\n"
        "5️⃣ <b>💬 Xabarlarim</b> bo'limida o'qing"
    )
    await message.answer(text, parse_mode="HTML")

# ============================================================
# /menu
# ============================================================
@dp.message(Command("menu"))
async def cmd_menu(message: types.Message, state: FSMContext) -> None:
    pending_anonymous_targets.pop(message.from_user.id, None)
    pending_reply_targets.pop(message.from_user.id, None)
    await state.clear()
    await message.answer(
        "📋 <b>Bosh menyu</b>",
        parse_mode="HTML",
        reply_markup=reply_keyboard(),
    )
    await message.answer("Quyidagi menyudan tanlang:", reply_markup=main_menu_keyboard())

# ============================================================
# /profile
# ============================================================
@dp.message(Command("profile"))
async def cmd_profile(message: types.Message) -> None:
    user = db.get_user(message.from_user.id)
    if not user:
        await message.answer("❌ Foydalanuvchi topilmadi")
        return
    text = (
        f"👤 <b>Sizning profilingiz</b>\n\n"
        f"🆔 ID: <code>{user['user_id']}</code>\n"
        f"👤 Username: @{user.get('username') or '—'}\n"
        f"📛 Ism: {user.get('first_name','')} {user.get('last_name','')}\n"
        f"💬 Qabul qilingan xabarlar: {user['message_count']}\n"
    )
    await message.answer(text, parse_mode="HTML")

# ============================================================
# /messages
# ============================================================
@dp.message(Command("messages"))
async def cmd_messages(message: types.Message) -> None:
    messages = db.get_user_messages(message.from_user.id)
    if not messages:
        await message.answer("📭 Hozircha xabar yo'q.")
        return
    for msg in messages:
        text = f"💬 <b>Anonim xabar</b>:\n\n{msg['message_text']}\n\n<i>🕐 {msg['created_at']}</i>"
        await message.answer(
            text,
            parse_mode="HTML",
            reply_markup=message_actions_markup(msg['message_id'], msg['sender_id'])
        )

# ============================================================
# /cancel
# ============================================================
@dp.message(Command("cancel"))
async def cmd_cancel(message: types.Message, state: FSMContext) -> None:
    pending_anonymous_targets.pop(message.from_user.id, None)
    pending_reply_targets.pop(message.from_user.id, None)
    await state.clear()
    await message.answer(
        "❌ Bekor qilindi.\n/menu — Bosh menyuga qaytish.",
        reply_markup=reply_keyboard(),
    )

# ============================================================
# /admin
# ============================================================
@dp.message(Command("admin"))
async def cmd_admin(message: types.Message) -> None:
    if not is_admin(message.from_user.id):
        await message.answer("❌ Siz admin emassiz.")
        return
    await message.answer(
        "🛠 <b>Admin panel</b>",
        parse_mode="HTML",
        reply_markup=admin_menu_keyboard(),
    )

# ============================================================
# Inline callback — admin
# ============================================================
@dp.callback_query(F.data == "admin_user_count")
async def cb_admin_user_count(callback: types.CallbackQuery) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q", show_alert=True)
        return
    count = db.get_all_users_count()
    await callback.message.edit_text(
        f"👥 Jami foydalanuvchilar: <b>{count}</b>",
        parse_mode="HTML",
        reply_markup=admin_menu_keyboard(),
    )
    await callback.answer()

@dp.callback_query(F.data == "admin_broadcast")
async def cb_admin_broadcast_start(callback: types.CallbackQuery, state: FSMContext) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q", show_alert=True)
        return
    await state.set_state(AdminStates.broadcast_text)
    await callback.message.answer(
        "📢 Hammaga yuboriladigan xabarni yozing.\nBekor qilish uchun /cancel"
    )
    await callback.answer()

@dp.message(AdminStates.broadcast_text)
async def handle_broadcast(message: types.Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        return
    await state.clear()
    if not hasattr(db, "get_all_user_ids"):
        await message.answer("❌ get_all_user_ids metodi database.py da yo'q. Qo'shing.")
        return
    user_ids = db.get_all_user_ids()
    sent = failed = 0
    for uid in user_ids:
        try:
            await bot.send_message(uid, f"📢 <b>E'lon:</b>\n\n{message.text}", parse_mode="HTML")
            sent += 1
        except Exception:
            failed += 1
    await message.answer(f"✅ Yuborildi: {sent}\n❌ Yuborilamadi: {failed}")

# ============================================================
# Admin: Channel management
# ============================================================
@dp.callback_query(F.data == "admin_add_channel")
async def cb_admin_add_channel(callback: types.CallbackQuery, state: FSMContext) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q", show_alert=True)
        return
    await state.set_state(AdminStates.adding_channel)
    await callback.message.answer(
        "📢 <b>Kanal qo'shish</b>\n\n"
        "Iltimos, kanal username'ini yuboring (masalan: @channelname) "
        "yoki kanaldan birorta xabarni forward qiling.",
        parse_mode="HTML"
    )
    await callback.answer()

@dp.message(AdminStates.adding_channel, ~F.text.in_(CONTROL_BUTTON_LABELS))
async def handle_add_channel(message: types.Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        await state.clear()
        return

    channel_id = None
    channel_username = None
    invite_link = None
    chat = None

    # Case 1: forwarded message from channel
    if message.forward_from_chat:
        chat = message.forward_from_chat
        channel_id = chat.id
        channel_username = chat.username  # None for private channels
    # Case 2: text input (username, URL, invite link)
    elif message.text:
        raw = message.text.strip()
        is_private_invite = False

        # Detect private invite links
        if raw.startswith('https://t.me/+'):
            is_private_invite = True
            invite_link = raw
        elif raw.startswith('https://t.me/joinchat/'):
            is_private_invite = True
            invite_link = raw
        elif 't.me/+' in raw:
            is_private_invite = True
            invite_link = raw
        elif 'joinchat/' in raw:
            is_private_invite = True
            invite_link = raw

        if is_private_invite:
            # Private invite link: just capture it; chat resolution is done via check_chat_invite_link to get chat object
            try:
                invite_info = await bot.check_chat_invite_link(invite_link)
                if invite_info and invite_info.chat:
                    chat = invite_info.chat
                    channel_id = chat.id
                    channel_username = None  # Private channels have no username
                else:
                    await message.answer("❌ Invite link noto'g'ri yoki muddati o'tgan.")
                    return
            except Exception:
                await message.answer("❌ Invite linkni tekshirib bo'lmadi.")
                return
        else:
            # Public channel: extract identifier
            identifier = raw
            if 't.me/' in identifier:
                parts = identifier.split('t.me/')
                if len(parts) > 1:
                    identifier = parts[1].strip('/')
                    if '?' in identifier:
                        identifier = identifier.split('?')[0]
                    if '/' in identifier:
                        identifier = identifier.split('/')[-1]
            elif identifier.startswith('@'):
                identifier = identifier[1:]

            if not identifier:
                await message.answer("❌ Kanal topilmadi. Noto'g'ri format.")
                return

            candidates = []
            if not identifier.startswith('@'):
                candidates.append(f"@{identifier}")
            candidates.append(identifier)
            for cand in candidates:
                try:
                    chat = await bot.get_chat(cand)
                    channel_id = chat.id
                    channel_username = (chat.username or '').lstrip('@') or identifier
                    break
                except Exception:
                    continue

    if not channel_id or not chat:
        await message.answer("❌ Kanal topilmadi. Iltimos, kanal username'ini yuboring yoki kanaldan xabar forward qiling.")
        return

    # Verify bot is admin
    try:
        bot_member = await bot.get_chat_member(chat_id=channel_id, user_id=bot.id)
        if bot_member.status not in ("administrator", "creator"):
            await message.answer("❌ Bot kanalda admin emas. Iltimos botni admin qiling.")
            return
    except Exception:
        await message.answer("❌ Bot kanalga kirish imkoni yo'q.")
        return

    # If private channel without username and no invite_link yet, ask for invite link
    if not channel_username and not invite_link:
        await state.update_data(pending_channel_id=channel_id)
        await state.set_state(AdminStates.waiting_channel_invite)
        await message.answer(
            "🔗 Ushbu kanal private (username yo'q).\n"
            "Iltimos, kanalga qo'shilish invite linkini yuboring:\n"
            "Misol: https://t.me/+xxxx"
        )
        return

    # Save channel directly (public or private with invite_link)
    success = db.add_required_channel(channel_id, channel_username, invite_link)
    if success:
        display_name = channel_username if channel_username else f"ID: {channel_id}"
        await message.answer(f"✅ Kanal qo'shildi: {display_name}")
    else:
        await message.answer("❌ Kanalni qo'shishda xatolik (balki allaqachon qo'shilgan?)")
    await state.clear()


# ============================================================
# Admin: Channel invite link collection (for private channels)
# ============================================================
@dp.message(AdminStates.waiting_channel_invite, ~F.text.in_(CONTROL_BUTTON_LABELS))
async def handle_channel_invite(message: types.Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        await state.clear()
        return

    raw = message.text.strip()

    # Minimal format validation — must look like t.me invite
    is_private_invite = (
        raw.startswith('https://t.me/+') or 
        raw.startswith('https://t.me/joinchat/') or
        't.me/+' in raw or
        'joinchat/' in raw
    )

    if not is_private_invite:
        await message.answer("❌ Noto'g'ri format. Iltimos, https://t.me/+xxxx yoki https://t.me/joinchat/xxxx formatida yuboring.")
        return

    # Retrieve pending channel_id from state
    data = await state.get_data()
    channel_id = data.get('pending_channel_id')
    if not channel_id:
        await message.answer("❌ Sessiya muddati tugagan. Qaytadan urinib ko'ring.")
        await state.clear()
        return

    # Save channel as private (no username) with the raw invite_link
    success = db.add_required_channel(channel_id, None, raw)
    if success:
        await message.answer(f"✅ Kanal qo'shildi (private). Invite link saqlandi.")
    else:
        await message.answer("❌ Kanalni qo'shishda xatolik.")

    await state.clear()

@dp.callback_query(F.data == "admin_remove_channel")
async def cb_admin_remove_channel(callback: types.CallbackQuery) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q", show_alert=True)
        return
    
    channels = db.get_required_channels()
    if not channels:
        await callback.message.edit_text(
            "📭 Hozircha majburiy kanallar yo'q.",
            reply_markup=admin_menu_keyboard()
        )
        await callback.answer()
        return

    rows = []
    for ch in channels:
        # Prefer username, else invite link snippet, else ID
        if ch.get('channel_username'):
            name = ch['channel_username']
        elif ch.get('invite_link'):
            # Show last part of invite link
            link = ch['invite_link']
            short = link.split('/')[-1] if '/' in link else link
            name = f"Invite: {short}"
        else:
            name = f"ID {ch['channel_id']}"
        rows.append([InlineKeyboardButton(text=f"🗑 {name}", callback_data=f"delete_channel_{ch['id']}")])
    rows.append([InlineKeyboardButton(text="🔄 Orqaga", callback_data="admin_menu")])

    await callback.message.edit_text(
        "🗑 <b>Kanalni o'chirish</b>\n\nO'chirish uchun tugmani bosing:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )
    await callback.answer()

@dp.callback_query(F.data == "admin_menu")
async def cb_admin_menu(callback: types.CallbackQuery) -> None:
    await callback.message.edit_text(
        "🛠 <b>Admin panel</b>",
        parse_mode="HTML",
        reply_markup=admin_menu_keyboard(),
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("delete_channel_"))
async def cb_delete_channel(callback: types.CallbackQuery) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q", show_alert=True)
        return
    try:
        ch_id = int(callback.data.split("_")[2])
    except (ValueError, IndexError):
        await callback.answer("❌ Xato", show_alert=True)
        return
    success = db.remove_required_channel(ch_id)
    if success:
        await callback.answer("✅ Kanal o'chirildi", show_alert=True)
    else:
        await callback.answer("❌ O'chirishda xatolik", show_alert=True)
    # Refresh list
    await cb_admin_remove_channel(callback)

# ============================================================
# Inline callback — asosiy menyu
# ============================================================
@dp.callback_query(F.data == "menu_get_link")
async def cb_get_link(callback: types.CallbackQuery) -> None:
    link = await get_personal_link(callback.from_user.id)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔗 Linkni ochish", url=link)],
        [InlineKeyboardButton(text="🔄 Orqaga",        callback_data="menu_main")],
    ])
    await callback.message.edit_text(
        f"📎 <b>Sizning shaxsiy linkingiz:</b>\n\n<code>{link}</code>\n\n"
        f"Nusxalab do'stlaringizga yuboring!",
        parse_mode="HTML",
        reply_markup=keyboard,
    )
    await callback.answer()

@dp.callback_query(F.data == "menu_profile")
async def cb_profile(callback: types.CallbackQuery) -> None:
    user = db.get_user(callback.from_user.id)
    if not user:
        await callback.answer("❌ Foydalanuvchi topilmadi", show_alert=True)
        return
    text = (
        f"👤 <b>Sizning profilingiz</b>\n\n"
        f"🆔 ID: <code>{user['user_id']}</code>\n"
        f"👤 Username: @{user.get('username') or '—'}\n"
        f"📛 Ism: {user.get('first_name','')} {user.get('last_name','')}\n"
        f"💬 Qabul qilingan xabarlar: {user['message_count']}\n"
    )
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Orqaga", callback_data="menu_main")],
        ]),
    )
    await callback.answer()



@dp.callback_query(F.data == "menu_view_messages")
async def cb_view_messages(callback: types.CallbackQuery) -> None:
    messages = db.get_user_messages(callback.from_user.id)
    if not messages:
        await callback.message.edit_text(
            "📭 Hozircha xabar yo'q.\n\nShaxsiy linkingizni ulashing!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📎 Linkni olish", callback_data="menu_get_link")],
                [InlineKeyboardButton(text="🔄 Orqaga",       callback_data="menu_main")],
            ]),
        )
        await callback.answer()
        return

    text = f"💬 <b>Sizda {len(messages)} ta xabar bor</b>\n\n"
    for i, msg in enumerate(messages[:5], 1):
        preview = msg["message_text"][:50] + ("..." if len(msg["message_text"]) > 50 else "")
        text += f"{i}. <i>{preview}</i>\n   📅 {msg['created_at']}\n\n"
    if len(messages) > 5:
        text += f"... va yana {len(messages) - 5} ta xabar"

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📖 Hammasini o'qish", callback_data="view_all_messages")],
            [InlineKeyboardButton(text="🔄 Orqaga",           callback_data="menu_main")],
        ]),
    )
    await callback.answer()

@dp.callback_query(F.data == "view_all_messages")
async def cb_view_all_messages(callback: types.CallbackQuery) -> None:
    messages = db.get_user_messages(callback.from_user.id)
    if not messages:
        await callback.answer("Xabar topilmadi", show_alert=True)
        return
    for msg in messages:
        text = f"💬 <b>Anonim xabar</b>:\n\n{msg['message_text']}\n\n<i>🕐 {msg['created_at']}</i>"
        await callback.message.answer(
            text,
            parse_mode="HTML",
            reply_markup=message_actions_markup(msg['message_id'], msg['sender_id'])
        )
    await callback.answer("✅ Barcha xabarlar ko'rsatildi")

@dp.callback_query(F.data == "menu_help")
async def cb_help(callback: types.CallbackQuery) -> None:
    await callback.message.edit_text(
        "🤖 <b>Qanday ishlaydi?</b>\n\n"
        "1️⃣ <b>Mening linkim</b> tugmasini bosing\n"
        "2️⃣ Linkni do'stlaringizga yuboring\n"
        "3️⃣ Ular linkga bosib sizga anonim xabar yuborishadi\n"
        "4️⃣ <b>Xabarlarim</b> bo'limida o'qing\n\n"
        "<b>Maxfiylik:</b>\n"
        "🔒 Sozlamalarda anonim xabarlarni o'chirishingiz mumkin\n"
        "⏱ Spam himoyasi mavjud",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Orqaga", callback_data="menu_main")],
        ]),
    )
    await callback.answer()

@dp.callback_query(F.data == "menu_main")
async def cb_main_menu(callback: types.CallbackQuery, state: FSMContext) -> None:
    pending_anonymous_targets.pop(callback.from_user.id, None)
    pending_reply_targets.pop(callback.from_user.id, None)
    await state.clear()
    await callback.message.edit_text(
        "🛠 <b>Admin panel</b>",
        parse_mode="HTML",
        reply_markup=admin_menu_keyboard(),
    )
    await callback.answer()

# ============================================================
# Inline callback — asosiy menyu
# ============================================================
# Subscription check callback
# ============================================================
@dp.callback_query(F.data == "subscription_check")
async def cb_subscription_check(callback: types.CallbackQuery) -> None:
    if await check_user_subscription(callback.from_user.id):
        await callback.message.edit_text("✅ Obuna tasdiqlandi! Endi botdan foydalanishingiz mumkin.")
        await callback.answer("✅ Muvaffaqiyatli", show_alert=True)
        # Show main menu
        await callback.message.answer("📋 <b>Bosh menyu</b>", parse_mode="HTML", reply_markup=main_menu_keyboard())
    else:
        await callback.answer("❌ Hali obuna bo'lmagansiz. Barcha kanallarga obuna bo'ling va qaytadan tekshring.", show_alert=True)

# Reply-ga tegishli vaqtinchalik xotira: reply_sender_id -> original_sender_id
pending_reply_targets: dict[int, int] = {}

# ============================================================
# Inline callback — Reply va Block
# ============================================================
@dp.callback_query(F.data.startswith("reply_start_"))
async def cb_reply_start(callback: types.CallbackQuery, state: FSMContext) -> None:
    message_id = int(callback.data.split("_")[2])
    msg = db.get_message_by_id(message_id)
    
    if not msg or not msg['sender_id']:
        await callback.answer("❌ Bu xabar uchun javob berish mumkin emas.", show_alert=True)
        return
    
    if msg['recipient_id'] != callback.from_user.id:
        await callback.answer("❌ Bu sizga tegishli xabar emas.", show_alert=True)
        return
    
    # Clear any pending anonymous target to avoid confusion
    pending_anonymous_targets.pop(callback.from_user.id, None)
    # Start reply mode
    pending_reply_targets[callback.from_user.id] = msg['sender_id']
    await state.update_data(reply_to_message_id=message_id)
    await state.set_state(MessageStates.waiting_for_reply)
    
    await callback.message.answer(
        f"↩️ <b>Javob yozmoqdasiz</b>\n\n"
        f"Javobingizni yozing (Hozirda botda faqat matnlar orqali habar yuborish mumkin).\n"
        f"Bekor qilish uchun <b>❌ Bekor qilish</b> tugmasni bosing.",
        parse_mode="HTML",
        reply_markup=reply_keyboard(),
    )
    await callback.answer()

@dp.message(F.text == "🔗 Mening linkim")
async def btn_my_link(message: types.Message, state: FSMContext) -> None:
    pending_anonymous_targets.pop(message.from_user.id, None)
    pending_reply_targets.pop(message.from_user.id, None)
    await state.clear()
    link = await get_personal_link(message.from_user.id)
    await message.answer(
        f"🔗 <b>Sizning anonim linkingiz:</b>\n\n<code>{link}</code>",
        parse_mode="HTML",
        reply_markup=reply_keyboard(),
    )

@dp.message(F.text == "🏠 Bosh menyu")
async def btn_menu_return(message: types.Message, state: FSMContext) -> None:
    pending_anonymous_targets.pop(message.from_user.id, None)
    pending_reply_targets.pop(message.from_user.id, None)
    await state.clear()
    await cmd_start(message, state)

@dp.message(F.text == "❌ Bekor qilish")
async def btn_cancel_action(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    is_admin_user = is_admin(message.from_user.id)
    pending_anonymous_targets.pop(message.from_user.id, None)
    pending_reply_targets.pop(message.from_user.id, None)
    await state.clear()
    if is_admin_user and current_state and current_state.startswith("AdminStates"):
        await message.answer("❌ Bekor qilindi.", reply_markup=admin_menu_keyboard())
    else:
        await message.answer("❌ Bekor qilindi.", reply_markup=reply_keyboard())

# ============================================================
# Anonim xabar qabul qilish — matn (FSM)
# ============================================================
@dp.message(MessageStates.waiting_for_message, ~F.text.in_(CONTROL_BUTTON_LABELS))
async def handle_anonymous_message(message: types.Message, state: FSMContext) -> None:
    # Only text messages
    if not message.text:
        await message.answer("❌ Faqat matn xabar yuborishingiz mumkin.")
        return

    if len(message.text) > MAX_MESSAGE_LENGTH:
        await message.answer(f"❌ Xabar juda uzun (maksimal {MAX_MESSAGE_LENGTH} belgi).")
        return

    sender_id    = message.from_user.id
    recipient_id = pending_anonymous_targets.get(sender_id)

    if recipient_id is None:
        await message.answer(
            "❌ Faol qabul qiluvchi topilmadi. Linkni qayta oching.",
        )
        await state.clear()
        return

    # Rate limit tekshirish
    if not db.check_rate_limit(sender_id, RATE_LIMIT_MESSAGES, RATE_LIMIT_SECONDS):
        await message.answer(
            f"⏱ Juda tez xabar yuboryapsiz!\n"
            f"Maksimal: {RATE_LIMIT_MESSAGES} ta xabar / {RATE_LIMIT_SECONDS} soniya.\n"
            f"Biroz kuting."
        )
        return

    db.record_message_for_rate_limit(sender_id)

    # Save message to DB and get the message_id
    message_id = db.save_anonymous_message(
        recipient_id=recipient_id,
        message_text=message.text,
        sender_id=sender_id
    )
    
    if message_id:
        pending_anonymous_targets.pop(sender_id, None)
        await state.clear()

        await message.answer(
            "✅ <b>Xabar anonim tarzda yuborildi!</b>\n\n"
            "Davom etish uchun quyidagilardan birini tanlang 👇",
            parse_mode="HTML",
            reply_markup=reply_keyboard(),
        )

        # Qabul qiluvchiga xabar yuborish + 👀 reaksiya + inline keyboard
        try:
            sent_msg = await bot.send_message(
                recipient_id,
                f"📨 <b>Yangi anonim xabar!</b>\n\n"
                f"{message.text}\n\n"
                f"<i>🕐 {now_uz()}</i>",
                parse_mode="HTML",
                reply_markup=message_actions_markup(message_id, sender_id)
            )
            try:
                await bot.set_message_reaction(
                    chat_id=recipient_id,
                    message_id=sent_msg.message_id,
                    reaction=[types.ReactionTypeEmoji(emoji="👀")],
                )
            except Exception:
                pass
        except Exception as e:
            logger.warning(f"Qabul qiluvchiga xabar yuborib bo'lmadi {recipient_id}: {e}")

        logger.info(f"{sender_id} → {recipient_id} xabar muvaffaqiyatli yuborildi")
    else:
        await message.answer("❌ Xabar yuborishda xatolik. Qaytadan urinib ko'ving.")

# ============================================================
# Javob yuborish — matn (FSM)
# ============================================================
@dp.message(MessageStates.waiting_for_reply, F.text)
async def handle_reply_text(message: types.Message, state: FSMContext) -> None:
    sender_id = message.from_user.id
    recipient_id = pending_reply_targets.get(sender_id)
    if not recipient_id:
        await message.answer("❌ Faol qabul qiluvchi topilmadi.")
        await state.clear()
        return

    data = await state.get_data()
    reply_to_message_id = data.get('reply_to_message_id')

    # Rate limit
    if not db.check_rate_limit(sender_id, RATE_LIMIT_MESSAGES, RATE_LIMIT_SECONDS):
        await message.answer(
            f"⏱ Juda tez xabar yuboryapsiz!\n"
            f"Maksimal: {RATE_LIMIT_MESSAGES} ta xabar / {RATE_LIMIT_SECONDS} soniya.\n"
            f"Biroz kuting."
        )
        return
    db.record_message_for_rate_limit(sender_id)

    # Save reply
    message_id = db.save_anonymous_message(
        recipient_id=recipient_id,
        message_text=message.text,
        sender_id=sender_id,
        reply_to_message_id=reply_to_message_id
    )
    if message_id:
        pending_reply_targets.pop(sender_id, None)
        await state.clear()
        await message.answer(
            "✅ <b>Javob anonim tarzda yuborildi!</b>\n\n"
            "Davom etish uchun quyidagilardan birini tanlang 👇",
            parse_mode="HTML",
            reply_markup=reply_keyboard(),
        )
        try:
            sent_msg = await bot.send_message(
                recipient_id,
                f"📨 <b>Yangi anonim javob!</b>\n\n"
                f"{message.text}\n\n"
                f"<i>🕐 {now_uz()}</i>",
                parse_mode="HTML",
                reply_markup=message_actions_markup(message_id, sender_id)
            )
            try:
                await bot.set_message_reaction(
                    chat_id=recipient_id,
                    message_id=sent_msg.message_id,
                    reaction=[types.ReactionTypeEmoji(emoji="👀")],
                )
            except Exception:
                pass
        except Exception as e:
            logger.warning(f"Recipient {recipient_id} ga javob yuborib bo'lmadi: {e}")
    else:
        await message.answer("❌ Xabar yuborishda xatolik. Qaytadan urinib ko'ving.")

# ============================================================
# Boshqa xabarlar
# ============================================================
@dp.message()
async def handle_any_message(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state == MessageStates.waiting_for_message:
        await handle_anonymous_message(message, state)
    elif current_state == MessageStates.waiting_for_reply:
        if message.text:
            await handle_reply_text(message, state)
        else:
            await message.answer("❌ Faqat matn xabar yuborishingiz mumkin.")
    else:
        await message.answer(
            "👋 Anonim xabarlar boti!\n\n"
            "/start — Boshlash\n"
            "/help  — Yordam"
        )

# ============================================================
# Botni ishga tushirish
# ============================================================
async def main() -> None:
    logger.info("Anonim Xabarlar Boti ishga tushmoqda...")
    db.cleanup_old_rate_limit_entries()
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Bot foydalanuvchi tomonidan to'xtatildi")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    print("🤖 Anonim Xabarlar Boti ishga tushmoqda...")
    print("=" * 50)
    asyncio.run(main())