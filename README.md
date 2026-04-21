# 🛍️ Telegram Mini App Store (Full-Stack)

A complete, full-stack Telegram Mini App solution for selling digital products directly inside Telegram. It combines a seamless web-based frontend with a robust asynchronous Python backend and SQLite database.

## ✨ Features
- Telegram Web App Integration: Uses the official Telegram.WebApp API to open a native-looking digital storefront right inside the chat.
- Dynamic Cart Logic: Groups items, calculates totals, and securely transmits JSON payload from the frontend to the bot.
- Persistent Storage (SQLite): Automatically creates a local database (shop.db) and securely logs every user order, including Telegram User ID, username, and cart details.
- Beautiful Receipts: Parses raw cart data and generates clean, human-readable receipts formatted with Markdown/HTML.
- Adaptive UI: The frontend automatically adapts to the user's Telegram theme (Dark/Light mode).

## 🛠 Tech Stack
- Backend: Python 3.13, aiogram 3.x, aiosqlite (Async Database)
- Frontend: HTML5, CSS3, Vanilla JavaScript, GitHub Pages (Hosting)
- Storage: SQLite3

## ⚙️ How It Works
1. The user sends /start and clicks the [ 🛍 Open Store ] inline button.
2. A sleek Mini App opens, hosted via GitHub Pages.
3. The user adds items (e.g., Premium VPN, Game Keys) to their cart and clicks Checkout.
4. The Web App securely sends the JSON payload back to the bot.
5. The bot parses the data, saves the order into shop.db, and sends a beautifully formatted receipt to the user.

## 🚀 Setup Instructions
1. Clone the repository.
2. Add your Telegram Bot token to a token.txt file.
3. Change the WEB_APP_URL in bot.py to your hosted frontend URL.
4. Run the bot. The shop.db file will be generated automatically on the first run.

---
### Here is an example of how the bot works:
<img width="1167" height="984" alt="Screenshot 2026-04-21 224922" src="https://github.com/user-attachments/assets/81407a00-6d53-48c8-903a-c9a13b5baf4d" />


*Developed by [VelarixDev](https://github.com/VelarixDev)*
