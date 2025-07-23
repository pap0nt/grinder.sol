# 🧹 grinder.sol — Find your perfect Solana address, comrade

**grinder.sol** is a Telegram bot that grinds out beautiful Solana wallet addresses at warp speed. Want your address to start with `1SOL`, `DEAD`, or `1337BEEF`? Say no more.  
It uses `solana-keygen grind` under the hood, handles processes, dumps the keypair into your DMs, and vanishes like a ghost in the shell.

## 🔮 Features

- Generates vanity Solana addresses on demand (`/grind`)
- Telegram bot powered by `aiogram v3`
- Automatically sends you a `.json` file with your **private key**
- Async and concurrent — you can grind multiple at once
- CPU-limited — no server meltdowns
- Runs in Docker if you're into that DevOps life

## 🚀 Quickstart

```bash
git clone https://github.com/yourusername/grinder.sol.git
cd grinder.sol
cp .env.example .env
make build
make run
```

Or manually with Docker:
```
docker build -t solana-bot .
docker run --rm -it --cpus=1.0 --env-file .env solana-bot
```
Env configuration:
```
BOT_TOKEN=your_telegram_bot_token
SUPERADMIN_ID=your_tg_id("@getmyid_bot")
```

##  🤖 How to use
In Telegram:

```
/grind 1SOL
```

The bot will say “searching...”, spin up some threads, and send you a .json file with your shiny new keypair.

Use solana address or solana airdrop to flex that fresh wallet.

## 📦 Requirements
Python 3.11+

solana-keygen

aiogram v3

Docker (optional, but makes life easier)

## 🧠 Notes
Temporary key files are stored in /tmp and cleaned up.

Bot logs all grind requests (for science).

If it crashes — CTRL+C like a true hacker.

## ⚠️ Security Warning: Never store real funds in vanity wallets unless you're 100% sure you know what you're doing. This bot is for fun and experimentation — not cold storage.

## 👨‍💻 Author
Built at 3AM with zero sleep and maximum love:
@pap0nt

## License

This project is licensed under the [MIT License](./LICENSE).
