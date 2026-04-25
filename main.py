"""
Telegram Anonymous Messaging Bot
Allows users to send anonymous messages to each other via personal links

Main bot implementation using aiogram
"""

import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import asyncio

from config import TELEGRAM_BOT_TOKEN, RATE_LIMIT_MESSAGES, RATE_LIMIT_SECONDS
from database import DatabaseManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize database manager
db = DatabaseManager()

# Initialize bot and dispatcher
bot = Bot(token='8754049335:AAHlL451OBoPn6bFsye_dGyeoDESsH7dqNc')
dp = Dispatcher()

# Temporary in-memory map for anonymous message flows
pending_anonymous_targets: dict[int, int] = {}
CONTROL_BUTTON_LABELS = {"🔗 Mening linkim", "🏠 Menyuga qaytish"}

async def get_personal_link(user_id: int) -> str:
    """Return a personal start link using the bot's current username."""
    bot_info = await bot.get_me()
    return f"https://t.me/{bot_info.username}?start={user_id}"

# Define FSM states for conversation flow
class MessageStates(StatesGroup):
    """States for message sending flow"""
    waiting_for_recipient_id = State()
    waiting_for_message = State()


class UserStates(StatesGroup):
    """States for user settings flow"""
    main_menu = State()
    viewing_profile = State()


# ============================================================================
# START AND HELP COMMANDS
# ============================================================================

@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext) -> None:
    """
    Handle /start command
    - If user provides a referral ID in /start?start=USER_ID, they can send message to that user
    - Otherwise, register the user and show main menu
    """
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    
    # Register user in database
    db.register_user(user_id, username, first_name, last_name)
    logger.info(f"User {user_id} started the bot")
    
    # Check if start parameter was provided (referral/recipient ID)
    args = message.text.split()
    
    if len(args) > 1:
        # User clicked a referral link with start parameter
        recipient_id_str = args[1]
        
        try:
            recipient_id = int(recipient_id_str)
            
            # Check if recipient exists
            recipient = db.get_user(recipient_id)
            if not recipient:
                await message.answer(
                    "❌ The user you're trying to reach doesn't exist or hasn't started the bot yet.",
                    reply_markup=get_main_menu_keyboard()
                )
                return
            
            # Check if recipient is blocking anonymous messages
            if db.is_user_blocking_anonymous(recipient_id):
                await message.answer(
                    "❌ This user has disabled anonymous messages.",
                    reply_markup=get_main_menu_keyboard()
                )
                return
            
            # Store recipient ID in temporary in-memory mapping
            pending_anonymous_targets[user_id] = recipient_id
            await state.set_state(MessageStates.waiting_for_message)
            
            recipient_name = recipient.get('first_name') or recipient.get('username') or f"User {recipient_id}"
            await message.answer(
                f"✍️ You're about to send an anonymous message to {recipient_name}.\n\n"
                f"Send your message (max {4096} characters).\n\n"
                f"Type /cancel to go back.",
                reply_markup=get_after_send_keyboard()
            )
            return
        
        except ValueError:
            logger.warning(f"Invalid recipient ID provided: {recipient_id_str}")
            pass
    
    # Show main menu for normal start
    # yangi ✅
    bot_info = await bot.get_me()
    bot_username = bot_info.username
    user_link = f"https://t.me/{bot_username}?start={user_id}"
    
    welcome_text = (
        f"👋 Welcome to Anonymous Messages Bot!\n\n"
        f"Your personal link:\n"
        f"<code>{user_link}</code>\n\n"
        f"Share this link with friends so they can send you anonymous messages!\n\n"
        f"Use the menu below to get started."
    )
    
    await message.answer(welcome_text, parse_mode="HTML", reply_markup=get_after_send_keyboard())
    await message.answer("📋 <b>Main Menu</b>", parse_mode="HTML", reply_markup=get_main_menu_keyboard())
    await state.clear()


@dp.message(Command("help"))
async def cmd_help(message: types.Message) -> None:
    """Display help information"""
    help_text = (
        "🤖 <b>Anonymous Messages Bot Help</b>\n\n"
        "<b>Commands:</b>\n"
        "/start - Start the bot and see your personal link\n"
        "/help - Show this help message\n"
        "/menu - Show main menu\n"
        "/profile - View your profile\n"
        "/settings - Manage privacy settings\n"
        "/messages - View your received messages\n"
        "/cancel - Cancel current action\n\n"
        "<b>How to use:</b>\n"
        "1. Start the bot with /start\n"
        "2. Share your personal link with others\n"
        "3. Others can click your link and send you anonymous messages\n"
        "4. You'll receive messages without knowing who sent them\n\n"
        "<b>Features:</b>\n"
        "✅ Send anonymous messages via unique links\n"
        "✅ Rate limiting to prevent spam\n"
        "✅ Option to block anonymous messages\n"
        "✅ View message history\n"
    )
    await message.answer(help_text, parse_mode="HTML")


# ============================================================================
# MENU AND SETTINGS
# ============================================================================

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Generate main menu keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📬 My Link", callback_data="menu_get_link")],
        [InlineKeyboardButton(text="💬 View Messages", callback_data="menu_view_messages")],
        [InlineKeyboardButton(text="👤 Profile", callback_data="menu_profile")],
        [InlineKeyboardButton(text="⚙️ Settings", callback_data="menu_settings")],
        [InlineKeyboardButton(text="❓ Help", callback_data="menu_help")],
    ])
    return keyboard


def get_after_send_keyboard() -> types.ReplyKeyboardMarkup:
    """Generate the keyboard shown after sending an anonymous message."""
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="🔗 Mening linkim")],
            [types.KeyboardButton(text="🏠 Menyuga qaytish")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
    )
    return keyboard


@dp.callback_query(F.data == "menu_get_link")
async def cb_get_link(callback: types.CallbackQuery) -> None:
    """Show user their personal link"""
    user_id = callback.from_user.id
    user_link = await get_personal_link(user_id)
    
    text = (
        f"📎 <b>Your Personal Link</b>\n\n"
        f"<code>{user_link}</code>\n\n"
        f"Click the button below to copy it:\n"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Copy Link", url=user_link)],
        [InlineKeyboardButton(text="🔄 Back", callback_data="menu_main")],
    ])
    
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
    await callback.answer()


@dp.callback_query(F.data == "menu_profile")
async def cb_profile(callback: types.CallbackQuery) -> None:
    """Show user profile"""
    user_id = callback.from_user.id
    user = db.get_user(user_id)
    
    if not user:
        await callback.answer("❌ User not found", show_alert=True)
        return
    
    text = (
        f"👤 <b>Your Profile</b>\n\n"
        f"<b>User ID:</b> {user['user_id']}\n"
        f"<b>Username:</b> @{user['username']}\n"
        f"<b>Name:</b> {user['first_name']} {user['last_name']}\n"
        f"<b>Joined:</b> {user['created_at']}\n"
        f"<b>Messages Received:</b> {user['message_count']}\n"
        f"<b>Blocking Anonymous:</b> {'Yes ❌' if user['is_blocking_anonymous'] else 'No ✅'}\n"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Back", callback_data="menu_main")],
    ])
    
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
    await callback.answer()


@dp.callback_query(F.data == "menu_settings")
async def cb_settings(callback: types.CallbackQuery) -> None:
    """Show settings menu"""
    user_id = callback.from_user.id
    user = db.get_user(user_id)
    
    is_blocking = user['is_blocking_anonymous'] if user else False
    status = "✅ Enabled" if not is_blocking else "❌ Disabled"
    
    text = (
        f"⚙️ <b>Settings</b>\n\n"
        f"<b>Anonymous Messages:</b> {status}\n\n"
        f"Toggle whether you want to receive anonymous messages."
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🔒 Toggle Anonymous Messages",
            callback_data="settings_toggle_anonymous"
        )],
        [InlineKeyboardButton(text="🔄 Back", callback_data="menu_main")],
    ])
    
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
    await callback.answer()


@dp.callback_query(F.data == "settings_toggle_anonymous")
async def cb_toggle_anonymous(callback: types.CallbackQuery) -> None:
    """Toggle anonymous message blocking"""
    user_id = callback.from_user.id
    user = db.get_user(user_id)
    
    current_state = user['is_blocking_anonymous'] if user else False
    new_state = not current_state
    
    db.toggle_anonymous_blocking(user_id, new_state)
    
    if new_state:
        status = "❌ Disabled - You won't receive anonymous messages"
    else:
        status = "✅ Enabled - You can receive anonymous messages"
    
    await callback.answer(f"Setting updated!\n{status}", show_alert=True)
    await cb_settings(callback)


@dp.callback_query(F.data == "menu_view_messages")
async def cb_view_messages(callback: types.CallbackQuery) -> None:
    """Show user's received messages"""
    user_id = callback.from_user.id
    messages = db.get_user_messages(user_id)
    
    if not messages:
        text = "📭 You haven't received any messages yet.\n\nShare your personal link to get started!"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📎 Get Link", callback_data="menu_get_link")],
            [InlineKeyboardButton(text="🔄 Back", callback_data="menu_main")],
        ])
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
        await callback.answer()
        return
    
    # Show summary of messages
    text = f"💬 <b>You have {len(messages)} message(s)</b>\n\n"
    for i, msg in enumerate(messages[:5], 1):  # Show first 5 messages
        preview = msg['message_text'][:50] + "..." if len(msg['message_text']) > 50 else msg['message_text']
        text += f"{i}. <i>{preview}</i>\n   {msg['created_at']}\n\n"
    
    if len(messages) > 5:
        text += f"... and {len(messages) - 5} more messages"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📖 Read All Messages", callback_data="view_all_messages")],
        [InlineKeyboardButton(text="🔄 Back", callback_data="menu_main")],
    ])
    
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
    await callback.answer()


@dp.callback_query(F.data == "view_all_messages")
async def cb_view_all_messages(callback: types.CallbackQuery) -> None:
    """View all messages in detail"""
    user_id = callback.from_user.id
    messages = db.get_user_messages(user_id)
    
    if not messages:
        await callback.answer("No messages found", show_alert=True)
        return
    
    # Send each message as a separate message
    for msg in messages:
        text = (
            f"📨 <b>Anonymous Message</b>\n\n"
            f"{msg['message_text']}\n\n"
            f"<i>Received: {msg['created_at']}</i>"
        )
        await callback.message.answer(text, parse_mode="HTML")
        db.mark_message_as_read(msg['message_id'])
    
    await callback.answer("✅ All messages displayed")


@dp.callback_query(F.data == "menu_help")
async def cb_help(callback: types.CallbackQuery) -> None:
    """Show help from callback"""
    help_text = (
        "🤖 <b>How to Use</b>\n\n"
        "1️⃣ Click 'My Link' to get your personal link\n"
        "2️⃣ Share the link with friends\n"
        "3️⃣ They can click the link and send you anonymous messages\n"
        "4️⃣ You'll receive messages without knowing the sender\n"
        "5️⃣ Check 'View Messages' to read them\n\n"
        "<b>Privacy Features:</b>\n"
        "🔒 Toggle anonymous message blocking in Settings\n"
        "⏱️ Rate limiting prevents spam\n"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Back", callback_data="menu_main")],
    ])
    
    await callback.message.edit_text(help_text, parse_mode="HTML", reply_markup=keyboard)
    await callback.answer()


@dp.callback_query(F.data == "menu_main")
async def cb_main_menu(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Return to main menu"""
    pending_anonymous_targets.pop(callback.from_user.id, None)
    await state.clear()
    text = "📋 <b>Main Menu</b>\n\nSelect an option below:"
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_main_menu_keyboard())
    await callback.answer()


# ============================================================================
# MESSAGE HANDLING
# ============================================================================

@dp.message(Command("menu"))
async def cmd_menu(message: types.Message, state: FSMContext) -> None:
    """Show main menu"""
    pending_anonymous_targets.pop(message.from_user.id, None)
    await state.clear()
    text = "📋 <b>Main Menu</b>\n\nSelect an option below:"
    await message.answer(text, parse_mode="HTML", reply_markup=get_after_send_keyboard())
    await message.answer("Use the menu below or press a reply button:", reply_markup=get_main_menu_keyboard())


@dp.message(Command("profile"))
async def cmd_profile(message: types.Message) -> None:
    """Show profile command"""
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    if not user:
        await message.answer("❌ User not found")
        return
    
    text = (
        f"👤 <b>Your Profile</b>\n\n"
        f"<b>User ID:</b> {user['user_id']}\n"
        f"<b>Username:</b> @{user['username']}\n"
        f"<b>Name:</b> {user['first_name']} {user['last_name']}\n"
        f"<b>Messages Received:</b> {user['message_count']}\n"
    )
    await message.answer(text, parse_mode="HTML")


@dp.message(Command("messages"))
async def cmd_messages(message: types.Message) -> None:
    """Show messages command"""
    user_id = message.from_user.id
    messages = db.get_user_messages(user_id)
    
    if not messages:
        await message.answer("📭 You haven't received any messages yet.")
        return
    
    for msg in messages:
        text = (
            f"📨 <b>Anonymous Message</b>\n\n"
            f"{msg['message_text']}\n\n"
            f"<i>Received: {msg['created_at']}</i>"
        )
        await message.answer(text, parse_mode="HTML")
        db.mark_message_as_read(msg['message_id'])


@dp.message(Command("settings"))
async def cmd_settings(message: types.Message) -> None:
    """Show settings command"""
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    is_blocking = user['is_blocking_anonymous'] if user else False
    status = "✅ Enabled" if not is_blocking else "❌ Disabled"
    
    text = (
        f"⚙️ <b>Settings</b>\n\n"
        f"<b>Anonymous Messages:</b> {status}\n\n"
        f"Use /settings_toggle to change this setting."
    )
    await message.answer(text, parse_mode="HTML")


@dp.message(Command("settings_toggle"))
async def cmd_settings_toggle(message: types.Message) -> None:
    """Toggle anonymous messages via command"""
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    current_state = user['is_blocking_anonymous'] if user else False
    new_state = not current_state
    
    db.toggle_anonymous_blocking(user_id, new_state)
    
    if new_state:
        status = "❌ Disabled - You won't receive anonymous messages"
    else:
        status = "✅ Enabled - You can receive anonymous messages"
    
    await message.answer(f"✅ Setting updated!\n{status}")


@dp.message(MessageStates.waiting_for_message, ~F.text.in_(CONTROL_BUTTON_LABELS))
async def handle_message(message: types.Message, state: FSMContext) -> None:
    """Handle anonymous message input"""
    
    # Prevent control buttons from being processed as anonymous message text
    if message.text in CONTROL_BUTTON_LABELS:
        await message.answer(
            "🔔 Iltimos, menyu tugmalaridan birini tanlang yoki /menu buyrug'ini yuboring."
        )
        return

    # Check if message is too long
    if len(message.text) > 4096:
        await message.answer("❌ Message is too long (max 4096 characters)")
        return
    
    sender_id = message.from_user.id
    recipient_id = pending_anonymous_targets.get(sender_id)
    if recipient_id is None:
        await message.answer(
            "❌ No active anonymous recipient found. Please open the recipient's personal link again."
        )
        await state.clear()
        return
    
    # Check rate limit
    if not db.check_rate_limit(sender_id, RATE_LIMIT_MESSAGES, RATE_LIMIT_SECONDS):
        await message.answer(
            f"⏱️ You're sending messages too fast!\n"
            f"Maximum {RATE_LIMIT_MESSAGES} messages per {RATE_LIMIT_SECONDS} seconds.\n"
            f"Please wait a moment and try again."
        )
        return
    
    # Record message for rate limiting
    db.record_message_for_rate_limit(sender_id)
    
    # Check if recipient is still blocking
    if db.is_user_blocking_anonymous(recipient_id):
        await message.answer("❌ The recipient has disabled anonymous messages.")
        await state.clear()
        return
    
    # Save message to database
    if db.save_anonymous_message(recipient_id, message.text):
        pending_anonymous_targets.pop(sender_id, None)
        await state.clear()
        await message.answer(
            "✅ Xabar anonim tarzda yuborildi!\n\n"
            "Davom etish uchun quyidagilardan birini tanlang 👇",
            reply_markup=get_after_send_keyboard()
        )
        
        # Notify recipient
        recipient_user = db.get_user(recipient_id)
        recipient_name = recipient_user.get('first_name') if recipient_user else "Someone"
        
        try:
            await bot.send_message(
                recipient_id,
                f"📨 <b>You received an anonymous message:</b>\n\n"
                f"{message.text}\n\n"
                f"<i>Received: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>",
                parse_mode="HTML"
            )
        except Exception as e:
            logger.warning(f"Could not notify recipient {recipient_id}: {e}")
        
        logger.info(f"Message from {sender_id} to {recipient_id} sent successfully")
    else:
        await message.answer("❌ Failed to send message. Please try again.")


@dp.message(Command("cancel"))
async def cmd_cancel(message: types.Message, state: FSMContext) -> None:
    """Cancel current action"""
    pending_anonymous_targets.pop(message.from_user.id, None)
    await state.clear()
    await message.answer(
        "❌ Action cancelled.\n\nUse /menu to return to main menu.",
        reply_markup=get_after_send_keyboard()
    )


@dp.message(F.text == "🔗 Mening linkim")
async def btn_my_link(message: types.Message, state: FSMContext) -> None:
    """Send the user their dynamically generated personal link and clear anonymous state."""
    user_id = message.from_user.id
    pending_anonymous_targets.pop(user_id, None)
    await state.clear()

    personal_link = await get_personal_link(user_id)
    await message.answer(
        f"🔗 Sizning anonim linkingiz:\n\n{personal_link}",
        reply_markup=get_after_send_keyboard()
    )


@dp.message(F.text == "🏠 Menyuga qaytish")
async def btn_menu_return(message: types.Message, state: FSMContext) -> None:
    """Return the user to menu and clear anonymous state."""
    pending_anonymous_targets.pop(message.from_user.id, None)
    await state.clear()
    await cmd_start(message, state)


@dp.message(F.text == "❌ Bekor qilish")
async def btn_cancel_action(message: types.Message, state: FSMContext) -> None:
    """Clear pending anonymous state and confirm cancellation."""
    pending_anonymous_targets.pop(message.from_user.id, None)
    await state.clear()
    await message.answer(
        "❌ Bekor qilindi.",
        reply_markup=get_after_send_keyboard()
    )


@dp.message()
async def handle_any_message(message: types.Message, state: FSMContext) -> None:
    """Handle any other message"""
    current_state = await state.get_state()
    
    if current_state == MessageStates.waiting_for_message:
        # User is trying to send an anonymous message
        await handle_message(message, state)
    else:
        # Unknown message
        await message.answer(
            "👋 I'm an anonymous messaging bot!\n\n"
            "Use /start to begin or /help for more information."
        )


# ============================================================================
# MAIN BOT STARTUP
# ============================================================================

async def main() -> None:
    """Start the bot"""
    logger.info("Starting Anonymous Messages Bot...")
    
    # Clean up old rate limit entries
    db.cleanup_old_rate_limit_entries()
    
    try:
        # Start polling
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    print("🤖 Anonymous Messages Bot Starting...")
    print("=" * 50)
    print("Make sure your TELEGRAM_BOT_TOKEN is set in .env file")
    print("=" * 50)
    asyncio.run(main())
