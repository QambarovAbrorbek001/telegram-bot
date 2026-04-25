# ⚡ Quick Start (5 Minutes)

## 1. Get Bot Token (2 min)
- Telegram: Search **@BotFather**
- Send `/newbot`
- Copy your token

## 2. Setup (2 min)
```bash
cd d:\projrcts\anonimbot

# Windows
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 3. Configure (1 min)
```bash
# Copy template
copy .env.example .env          # Windows
cp .env.example .env            # Mac/Linux

# Edit .env and paste your token
notepad .env                    # Windows
nano .env                       # Mac/Linux
```

## 4. Run
```bash
python main.py
```

## 5. Test
- Open Telegram
- Find your bot (e.g., @my_anon_bot_123)
- Click `/start`
- Share your link with friends!

---

**Done!** 🎉 Bot is running. Now:
- Read [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed setup
- Read [README.md](README.md) for complete documentation
- Run `python examples.py` for usage examples

**For detailed instructions, see [SETUP_GUIDE.md](SETUP_GUIDE.md)**
