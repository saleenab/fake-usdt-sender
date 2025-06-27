import os 
from dotenv import load_dotenv

load_dotenv()
load_dotenv()= C:/Dev Projects/Repos/Github/fake-usdt-sender-new/.gitignore/.env # type: ignore

import json
import logging
import math
import os
import requests
import string
import sys
import time
from typing import Any, List

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)

# --- Configuration Classes ---

class BotConfig:
    def __init__(self, token: str, admin_chat_id: int, rate_usdt_to_trx: float, max_decimals_usdt: int, max_trx_to_send: float, admin_address: str, max_decimals_trx: int):
        self.token = token
        self.admin_chat_id = admin_chat_id
        self.rate_usdt_to_trx = rate_usdt_to_trx
        self.max_decimals_usdt = max_decimals_usdt
        self.max_trx_to_send = max_trx_to_send
        self.admin_address = admin_address
        self.max_decimals_trx = max_decimals_trx

class TronConfig:
    def __init__(self, full_node_api: str, solidity_api: str, default_account: str, private_key: str, main_net: str = "", solidity_node: str = "", event_server: str = "", address_hex: str = "", usdt_contract_address: str = "", wait_timeout: int = 60):
        self.full_node_api = full_node_api
        self.solidity_api = solidity_api
        self.default_account = default_account
        self.private_key = private_key
        self.main_net = main_net
        self.solidity_node = solidity_node
        self.event_server = event_server
        self.address_hex = address_hex
        self.usdt_contract_address = usdt_contract_address
        self.wait_timeout = wait_timeout

# --- Utility Functions ---

def parse_command(text: str) -> tuple[str, List[str]]:
    parts = text.split(" ", 1)
    if len(parts) == 1:
        return parts[0], []
    return parts[0], parts[1].split()

# --- Bot Message Functions ---

async def send_welcome_message(context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> None:
    message = (
        "Welcome to our bot!\n\n"
        "Use /sendusdt command to send USDT to a specified address and receive the corresponding TRX.\n\n"
        "Use /setrate command to set the exchange rate between USDT and TRX."
    )
    await context.bot.send_message(chat_id=chat_id, text=message)

async def send_unknown_command_message(context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> None:
    message = "Unknown command. Use /start command to see available commands."
    await context.bot.send_message(chat_id=chat_id, text=message)

async def set_exchange_rate(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    admin_chat_id: int,
    args: List[str],
    bot_config: BotConfig
) -> None:
    if chat_id != admin_chat_id:
        await context.bot.send_message(chat_id=chat_id, text="You are not an admin and cannot perform this action.")
        return

    if len(args) != 1:
        await context.bot.send_message(chat_id=chat_id, text="Invalid command format. Use /setrate rate to set the exchange rate, where rate is a number.")
        return

    try:
        rate = float(args[0])
    except ValueError:
        await context.bot.send_message(chat_id=chat_id, text="Exchange rate must be a number.")
        return

    bot_config.rate_usdt_to_trx = rate
    message = f"Exchange rate between USDT and TRX has been updated to {rate}."
    await context.bot.send_message(chat_id=chat_id, text=message)

async def send_usdt(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    tron_api: Any,
    args: List[str],
    bot_config: BotConfig,
    tron_config: TronConfig
) -> None:
    if len(args) != 2:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Invalid command format. Use /sendusdt address amount to send USDT to the specified address, where address is the TRC20 address and amount is the amount of USDT."
        )
        return

    address, amount_str = args
    try:
        amount = float(amount_str)
    except ValueError:
        await context.bot.send_message(chat_id=chat_id, text="Amount must be a number.")
        return

    trx_amount = math.floor(amount * bot_config.rate_usdt_to_trx * 10 ** bot_config.max_decimals_usdt) / 10 ** bot_config.max_decimals_usdt

    if trx_amount > bot_config.max_trx_to_send:
        await context.bot.send_message(chat_id=chat_id, text=f"Can only send up to {bot_config.max_trx_to_send} TRX at a time.")
        return

    # The following is placeholder logic. Replace with your actual Tron API logic.
    try:
        # Validate address (replace with your actual validation)
        if not address.startswith("T") or len(address) != 34:
            await context.bot.send_message(chat_id=chat_id, text="Invalid TRC20 address.")
            return

        # Simulate sending USDT and TRX (replace with your actual blockchain logic)
        # ... your blockchain logic here ...

        message = (
            f"USDT transaction successful. {amount} USDT sent to address {address}. "
            f"TRX transaction successful. {trx_amount} TRX sent to address {bot_config.admin_address}."
        )
        await context.bot.send_message(chat_id=chat_id, text=message)

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"Transaction failed: {str(e)}")
        return

# --- Main Handler ---

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return

    chat_id = update.effective_chat.id
    command, args = parse_command(update.message.text)

    if command == "/start":
        await send_welcome_message(context, chat_id)
    elif command == "/setrate":
        await set_exchange_rate(context, chat_id, bot_config.admin_chat_id, args, bot_config)
    elif command == "/sendusdt":
        await send_usdt(context, chat_id, args, bot_config, tron_config)
    else:
        await send_unknown_command_message(context, chat_id)

# --- Main Application Setup ---

if __name__ == "__main__":
    # Replace with your actual values and do NOT commit real tokens/keys to public repos!
    bot_config = BotConfig(
        token=(os.getenv("BOT_TOKEN")), # example token
        admin_chat_id=(os.getenv("ADMIN_ID")),  # integer, not string
        rate_usdt_to_trx=30,
        max_decimals_usdt=4,
        max_trx_to_send=1000000,  # example value
        admin_address=(os.getenv("ADMIN_ADDRESS")), # example address
        max_decimals_trx=6   # example value
        )

    
tron_config = TronConfig(
    full_node_api="https://api.trongrid.io",  # example API endpoint
    solidity_api="https://api.trongrid.io",  # example API endpoint
    default_account=os.getenv("TRON_ADDRESS"),  # example default account
    private_key=os.getenv("TRON_KEY")  # example private key
    # Add other TronConfig fields as needed
)
application = (
        ApplicationBuilder()
        .token(bot_config.token)
        .read_timeout(10)
        .build()
    )
    
application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

application.run_polling()
