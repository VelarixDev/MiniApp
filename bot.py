import asyncio
import json
import logging
import aiosqlite
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

# Configuration
TOKEN_FILE = "token.txt"
WEB_APP_URL = "https://velarixdev.github.io/MiniApp/"
DB_NAME = "shop.db"

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_db():
    """Initializes the database and creates the orders table if it doesn't exist."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                order_data TEXT
            )
        ''')
        await db.commit()
    logger.info("Database initialized successfully.")

async def save_order(user_id: int, username: str, order_data: str):
    """Saves the order data into the SQLite database."""
    try:
        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute(
                "INSERT INTO orders (user_id, username, order_data) VALUES (?, ?, ?)",
                (user_id, username, order_data)
            )
            await db.commit()
        logger.info(f"Order saved for user {user_id}")
    except Exception as e:
        logger.error(f"Failed to save order to DB: {e}")
        raise

def get_token():
    """Reads the bot token from the token.txt file."""
    try:
        with open(TOKEN_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        logger.error(f"Error: {TOKEN_FILE} not found.")
        raise Exception(f"{TOKEN_FILE} not found. Please create it and add your token.")
    except Exception as e:
        logger.error(f"Error reading token: {e}")
        raise

async def start_command(message: types.Message):
    """Handler for /start command."""
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛍 Открыть магазин", web_app=WebAppInfo(url="https://velarixdev.github.io/MiniApp/web/index.html"))]
        ],
        resize_keyboard=True
    )
    await message.answer("Привет! Нажми на кнопку ниже, чтобы перейти в наш магазин.", reply_markup=kb)

async def web_app_data_handler(message: types.Message):
    """Handler for receiving data from the Web App."""
    raw_data = ""
    try:
        # Extracting JSON data from the WebApp message
        raw_data = message.web_app_data.data
        order_json = json.loads(raw_data)

        # Determine if we have a list of items directly or inside a dictionary
        items_list = []
        if isinstance(order_json, list):
            items_list = order_json
        elif isinstance(order_json, dict):
            # Try common keys for the items list
            for key in ['items', 'cart', 'products', 'data']:
                if key in order_json and isinstance(order_json[key], list):
                    items_list = order_json[key]
                    break
            else:
                # If no common key is found, but it's a dict, maybe the dict itself is an item? 
                # (Unlikely for a cart, but let's handle it)
                items_list = [order_json]

        if not items_list:
            raise ValueError("No valid list of items found in JSON data.")

        # Grouping items by ID and calculating quantities/totals
        items_map = {}
        for item in items_list:
            item_id = item.get('id')
            if item_id is None:
                continue
            
            name = item.get('name', 'Unknown Item')
            try:
                price = float(item.get('price', 0.0))
            except (TypeError, ValueError):
                price = 0.0
                
            try:
                qty = int(item.get('qty', 1))
            except (TypeError, ValueError):
                qty = 1

            if item_id not in items_map:
                items_map[item_id] = {
                    'id': item_id,
                    'name': name,
                    'price': price,
                    'qty': 0
                }
            items_map[item_id]['qty'] += qty

        # Building the receipt and calculating total price
        receipt_lines = []
        total_price = 0.0
        for item in items_map.values():
            line_total = item['price'] * item['qty']
            total_price += line_total
            receipt_lines.append(f"🔹 {item['name']} (x{item['qty']}) — ${line_total:.2f}")

        if not receipt_lines:
             raise ValueError("The cart is empty.")

        receipt_body = "\n".join(receipt_lines)
        formatted_message = (
            f"✅ Ваш заказ успешно оформлен!\n"
            f"📦 Корзина:\n"
            f"{receipt_body}\n"
            f"💳 Итого к оплате: ${total_price:.2f}"
        )

        # Save the processed order to database
        await save_order(
            user_id=message.from_user.id,
            username=message.from_user.username or "Unknown",
            order_data=json.dumps(list(items_map.values()), ensure_ascii=False)
        )

        await message.answer(formatted_message, parse_mode="Markdown")

    except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON from WebApp data: {raw_data}")
        await message.answer("❌ Ошибка: Некорректные данные от магазина.")
    except Exception as e:
        logger.error(f"Error processing web_app_data: {e}")
        await message.answer("❌ Произошла ошибка при оформлении заказа. Попробуйте позже.")

async def main():
    # Initialize DB
    await init_db()

    # Get Token
    token = get_token()
    
    # Initialize Bot and Dispatcher
    bot = Bot(token=token)
    dp = Dispatcher()

    # Register Handlers
    # Correcting registration for aiogram 3.x style:
    dp.message.register(start_command, Command("start"))
    dp.message.register(web_app_data_handler, F.web_app_data)

    logger.info("Bot is starting...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Bot stopped due to error: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())