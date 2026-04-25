# 📑 Project Index & Navigation Guide

Welcome to the Telegram Anonymous Messages Bot! This file helps you navigate all the documentation and code.

## 🎯 Quick Navigation

### ⚡ Just Want to Get Started?
1. Read: [QUICKSTART.md](QUICKSTART.md) (2 min read)
2. Run: `install.bat` (Windows) or `bash install.sh` (Linux/Mac)
3. Configure your bot token in `.env`
4. Run: `python main.py`

### 📖 Want Detailed Setup Instructions?
1. Read: [SETUP_GUIDE.md](SETUP_GUIDE.md) - Complete step-by-step guide
2. Includes troubleshooting and common issues
3. Multiple OS-specific instructions

### 🔧 Want to Understand the Code?
1. Read: [DEVELOPMENT.md](DEVELOPMENT.md) - Technical reference
2. Complete API documentation
3. Architecture diagrams and code examples

### 🤔 Have Questions?
1. Check: [README.md](README.md) - FAQ section
2. Read: [DEVELOPMENT.md](DEVELOPMENT.md) - Troubleshooting
3. Review: [examples.py](examples.py) - Code examples

---

## 📁 Project Structure

```
telegram-anon-bot/
│
├── 📘 Documentation
│   ├── README.md                 ⭐ Main documentation & FAQ
│   ├── QUICKSTART.md             ⚡ 5-minute setup
│   ├── SETUP_GUIDE.md            📖 Detailed step-by-step guide
│   ├── DEVELOPMENT.md            🔧 Technical reference
│   └── INDEX.md                  📑 This file (navigation guide)
│
├── 🤖 Bot Code
│   ├── main.py                   🎯 Main bot handler (~1200 lines)
│   ├── database.py               🗄️ Database management (~400 lines)
│   ├── config.py                 ⚙️ Configuration & settings
│   └── admin.py                  👨‍💼 Admin utilities & statistics
│
├── 🧪 Development Files
│   ├── examples.py               📝 Usage examples & tests
│   ├── requirements.txt           📦 Python dependencies
│   └── .gitignore                🔐 Git ignore rules
│
├── 🚀 Setup & Execution Scripts
│   ├── install.bat               🪟 Windows auto-installer
│   ├── install.sh                🐧 Linux/Mac auto-installer
│   ├── run_bot.bat               🪟 Windows bot launcher
│   └── run_bot.sh                🐧 Linux/Mac bot launcher
│
└── ⚙️ Configuration
    ├── .env                      🔑 Your bot token (DON'T SHARE!)
    └── .env.example              📋 Example configuration template
```

---

## 📚 Documentation Guide

### README.md
**Best for:** Overview, features, FAQ, and general information
- ✅ Features list
- ✅ Installation overview
- ✅ Command reference
- ✅ Deployment options
- ✅ FAQ section
- ✅ API reference

**Read this if you:**
- Want to understand what the bot does
- Have general questions
- Want to know about features
- Need deployment help

---

### QUICKSTART.md
**Best for:** Getting up and running in 5 minutes
- ✅ Minimal setup steps
- ✅ All commands in one place
- ✅ References to other docs
- ✅ Links to detailed guides

**Read this if you:**
- Are experienced with Python
- Want to get started immediately
- Know what Telegram bots are

---

### SETUP_GUIDE.md
**Best for:** Detailed, step-by-step setup for beginners
- ✅ Complete setup instructions
- ✅ Multiple OS guides (Windows, Mac, Linux)
- ✅ Screenshot-like descriptions
- ✅ Extensive troubleshooting
- ✅ Each step explained
- ✅ Success checklist

**Read this if you:**
- Are new to Python or bot development
- Want detailed explanations
- Need troubleshooting help
- Prefer step-by-step guides

---

### DEVELOPMENT.md
**Best for:** Technical reference and code modifications
- ✅ Architecture diagrams
- ✅ Complete API reference
- ✅ Database schema & queries
- ✅ Code examples
- ✅ Message flow diagrams
- ✅ Extension guide
- ✅ Performance tips
- ✅ Deployment options

**Read this if you:**
- Want to modify the code
- Need technical details
- Are adding new features
- Want to understand architecture
- Need to deploy to production

---

### examples.py
**Best for:** Learning how to use the code
- ✅ Testing functions
- ✅ Database operation examples
- ✅ Admin panel examples
- ✅ User flow examples
- ✅ Error handling examples
- ✅ Configuration examples

**Read this if you:**
- Want to see code in action
- Need usage examples
- Want to test features
- Are learning the API

**Run examples:**
```bash
python -c "from examples import test_database_operations; test_database_operations()"
```

---

## 🚀 Getting Started Paths

### Path 1: Absolute Beginner
```
1. SETUP_GUIDE.md (Step 1-10)
2. Run: install.bat or bash install.sh
3. Configure .env
4. Run: python main.py
5. Test in Telegram
```

### Path 2: Experienced Developer
```
1. QUICKSTART.md (5 min)
2. Run: python -m venv venv && source venv/bin/activate
3. pip install -r requirements.txt
4. Configure .env with bot token
5. python main.py
```

### Path 3: Code Reviewer
```
1. README.md (overview)
2. main.py (read code)
3. database.py (understand database)
4. config.py (understand config)
5. DEVELOPMENT.md (technical details)
```

### Path 4: Production Deployment
```
1. README.md (deployment section)
2. DEVELOPMENT.md (deployment section)
3. docker build -t telegram-anon-bot .
4. docker run -e TELEGRAM_BOT_TOKEN=... telegram-anon-bot
```

---

## 🎓 Learning Path

### Level 1: User
- Use the bot
- Share your personal link
- Send/receive anonymous messages
- Manage settings

### Level 2: Administrator
- Run the bot yourself
- Monitor statistics (admin.py)
- Manage database
- Configure settings (config.py)

### Level 3: Developer
- Modify code (main.py)
- Add new features
- Extend database schema
- Customize keyboards/buttons

### Level 4: DevOps/SysAdmin
- Deploy to production
- Set up monitoring
- Configure backups
- Scale horizontally

---

## 📞 File Purpose Summary

### Code Files
| File | Purpose | Lines | Complexity |
|------|---------|-------|-----------|
| main.py | Bot handlers & commands | ~1200 | High |
| database.py | Database operations | ~400 | Medium |
| config.py | Configuration | ~40 | Low |
| admin.py | Admin utilities | ~250 | Medium |
| examples.py | Usage examples | ~300 | Medium |

### Setup Files
| File | Purpose | Run With |
|------|---------|----------|
| install.bat | Windows installer | `install.bat` |
| install.sh | Linux/Mac installer | `bash install.sh` |
| run_bot.bat | Windows launcher | `run_bot.bat` |
| run_bot.sh | Linux/Mac launcher | `bash run_bot.sh` |

### Configuration Files
| File | Purpose | Contains |
|------|---------|----------|
| requirements.txt | Python dependencies | Package list |
| .env.example | Template for .env | Example config |
| .env | Actual config | Your bot token |
| .gitignore | Git exclusions | Files to ignore |

---

## 🔑 Key Features

✅ **Personal Links** - Each user gets unique link
✅ **Anonymous Messaging** - Sender identity hidden
✅ **Rate Limiting** - Prevent spam (10 msgs/min)
✅ **Privacy Controls** - Users can block anonymous
✅ **Message History** - View all messages
✅ **SQLite Database** - Persistent storage
✅ **Modern Async** - High performance with aiogram 3.x
✅ **Well Documented** - Extensive comments & guides
✅ **Easy Setup** - Auto-installers included
✅ **Production Ready** - Deployment examples

---

## 🛠️ Common Tasks

### Change Rate Limit
Edit `config.py`:
```python
RATE_LIMIT_MESSAGES = 5   # Changed from 10
RATE_LIMIT_SECONDS = 30   # Changed from 60
```

### Add New Command
Edit `main.py`:
```python
@dp.message(Command("mycommand"))
async def cmd_mycommand(message: types.Message) -> None:
    await message.answer("Response")
```

### View Statistics
```bash
python -c "from admin import AdminPanel; AdminPanel().print_stats()"
```

### Backup Database
```bash
copy bot_database.db bot_database.backup.db  # Windows
cp bot_database.db bot_database.backup.db    # Linux/Mac
```

### Reset Database
```bash
del bot_database.db     # Windows
rm bot_database.db      # Linux/Mac
# Run bot again - new database created
```

---

## 🔐 Security Checklist

- [ ] Bot token in `.env` file
- [ ] `.env` added to `.gitignore`
- [ ] Never commit `.env` to git
- [ ] Regular database backups
- [ ] Monitor rate limiting
- [ ] Review user activity (admin.py)
- [ ] Update dependencies: `pip install --upgrade -r requirements.txt`
- [ ] Use strong bot username (hard to guess)

---

## 📈 Scalability

**SQLite works well for:**
- Up to 10,000+ users
- Millions of messages
- Single server deployment

**When to migrate to PostgreSQL:**
- Multiple bot instances
- > 100,000 users
- High-frequency queries
- Distributed deployment

---

## 🔗 External Links

- 🤖 [Telegram Bot API Docs](https://core.telegram.org/bots/api)
- 📚 [Aiogram Docs](https://docs.aiogram.dev/)
- 🐍 [Python Docs](https://docs.python.org/3/)
- 📦 [PyPI Packages](https://pypi.org/)

---

## 💡 Tips & Tricks

### Useful Commands
```bash
# Check Python version
python --version

# List installed packages
pip list

# Freeze current environment
pip freeze > requirements.txt

# Run in background (Linux/Mac)
nohup python main.py &

# Check if bot is running
ps aux | grep main.py

# Kill bot process
kill -9 <PID>

# View database
sqlite3 bot_database.db ".tables"
```

### IDE Setup
- **VS Code**: Install Python extension, select venv interpreter
- **PyCharm**: Mark venv/Lib/site-packages as Library Root
- **Sublime**: Install python3 build system

### Debugging
```python
# Add debug prints
print(f"DEBUG: {variable}")

# Use logging
import logging
logging.debug(f"Debug message: {data}")

# Use debugger
import pdb; pdb.set_trace()
```

---

## 📞 Support & Troubleshooting

### Before Asking for Help:
1. ✅ Read SETUP_GUIDE.md
2. ✅ Check README.md FAQ
3. ✅ Review error messages
4. ✅ Check logs: `python main.py 2>&1 | tee log.txt`
5. ✅ Review examples.py

### Common Issues:
- **Bot doesn't start** → Check .env file has token
- **No modules found** → Activate venv, pip install -r requirements.txt
- **Connection errors** → Check internet, firewall settings
- **Database locked** → Delete bot_database.db, restart bot

---

## 🎯 Next Steps

1. **Immediate** (Next 5 min)
   - Run installer script
   - Configure bot token
   - Start bot

2. **Short-term** (Next 1 hour)
   - Test in Telegram
   - Share link with friends
   - Receive messages

3. **Medium-term** (Next 1 day)
   - Read DEVELOPMENT.md
   - Understand code structure
   - Plan customizations

4. **Long-term** (Next 1 week)
   - Add custom features
   - Deploy to production
   - Monitor usage

---

## 📝 Version Info

- **Version**: 1.0 (Release)
- **Python**: 3.10+
- **Aiogram**: 3.2.0
- **Database**: SQLite3
- **Status**: ✅ Production Ready
- **Last Updated**: April 2024

---

## 📋 Checklist for First Run

- [ ] Python 3.10+ installed
- [ ] Bot token from @BotFather
- [ ] .env file configured
- [ ] Dependencies installed
- [ ] Bot starts without errors
- [ ] Can send message in Telegram
- [ ] Personal link works
- [ ] Can send anonymous message

---

**Happy Bot Building! 🚀**

For navigation help, use this file.
For setup help, read SETUP_GUIDE.md.
For code help, read DEVELOPMENT.md.
For overview, read README.md.

Start with [QUICKSTART.md](QUICKSTART.md) - takes 5 minutes!
