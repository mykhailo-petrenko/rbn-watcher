#!/usr/bin/env python

import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, html, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove, KeyboardButton,
)

from bot.Store import Store
from bot.Validator import validate_callsign_filter
from bot.types import SubscriptionDTO

# Bot token can be obtained via https://t.me/BotFather
TOKEN = getenv("BOT_API_KEY")
DB_CONNECTION_STRING = getenv("DB_CONNECTION_STRING")

store = Store(DB_CONNECTION_STRING)

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()
form_router = Router()


class From(StatesGroup):
    watch_filter_state = State()
    un_watch_filter_state = State()
    reset = State()


@form_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@form_router.message(Command("info"))
async def command_info_handler(message: Message, state: FSMContext) -> None:
    """
    This handler receives messages with `/info` command
    """
    await state.clear()
    chat_id = str(message.chat.id)
    subscriptions = store.get_subscriptions(chat_id)

    calls = [s[1] for s in subscriptions]
    indent = "    "
    calls = indent + f"\n{indent}".join(calls)
    n = len(subscriptions)

    await message.answer(
        f"""You have {html.bold(n)} subscriptions:\n{calls}"""
    )


@form_router.message(Command("watch"))
async def command_watch_handler(message: Message, state: FSMContext) -> None:
    """
    This handler receives messages with `/watch` command
    """
    await state.set_state(From.watch_filter_state)
    await message.answer(
        f"Enter the callsign",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(From.watch_filter_state)
async def command_watch_register_filter(message: Message, state: FSMContext) -> None:
    await state.clear()

    subscription = SubscriptionDTO()
    subscription.chat_id = str(message.chat.id)
    subscription.filter = message.text.upper()

    if not validate_callsign_filter(subscription.filter):
        await message.reply(f"Filter is invalid. Please enter valid callsign.")
        return

    store.add_subscription(subscription)

    await message.reply(f"Watching for '{subscription.filter}'")


@form_router.message(Command("unwatch"))
async def command_un_watch(message: Message, state: FSMContext) -> None:
    """
    This handler receives messages with `/unwatch` command
    """
    await state.set_state(From.un_watch_filter_state)
    await message.answer(
        f"Enter the filter (callsign) to unsubscribe",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(From.un_watch_filter_state)
async def command_un_watch_register_filter(message: Message, state: FSMContext) -> None:
    await state.clear()

    subscription = SubscriptionDTO()
    subscription.chat_id = str(message.chat.id)
    subscription.filter = message.text.upper()

    if not validate_callsign_filter(subscription.filter):
        await message.reply(f"Filter is invalid. Please enter valid callsign.")
        return

    store.remove_subscription(subscription)

    await message.reply(f"Unsubscribed from '{subscription.filter}'")


@form_router.message(Command("reset"))
async def command_reset_handler(message: Message, state: FSMContext) -> None:
    """
    This handler receives messages with `/reset` command
    """
    await state.set_state(From.reset)
    yes_no = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Yes"),
                KeyboardButton(text="No"),
            ]
        ],
        resize_keyboard=True,
    )

    await message.answer(
        f"Do you want to remove all subscriptions?",
        reply_markup=yes_no
    )


@form_router.message(From.reset, F.text.casefold() == "yes")
async def command_reset_handler_yes(message: Message, state: FSMContext) -> None:
    await state.clear()

    chat_id = str(message.chat.id)
    store.remove_all_subscriptions(chat_id)

    await message.answer(
        f"You unsubscribed successfully from all notifications.",
        reply_markup=ReplyKeyboardRemove()
    )


@form_router.message()
async def message_echo_handler(message: Message, state: FSMContext) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    await state.clear()
    logging.info(message.chat.id)
    try:
        # Send a copy of the received message
        await message.answer(
            message.text,
            reply_markup=ReplyKeyboardRemove()
        )
    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Nice try!")


async def main_loop() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp.include_router(form_router)
    # And the run events dispatching
    await init(bot)
    await dp.start_polling(bot)


async def init(bot) -> None:
    rows = store.get_all_subscribers()

    for row in rows:
        await bot.send_message(chat_id=int(row), text="Hi!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main_loop())
    print('bye ...')
