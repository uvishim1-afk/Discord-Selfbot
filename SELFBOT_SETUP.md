# Discord Selfbot Dashboard

A complete web-based dashboard for controlling your Discord selfbot. Everything runs on Railway.

## ⚠️ Important Security Notice

**NEVER SHARE YOUR USER TOKEN!**
- Your user token is like a password to your Discord account
- Anyone with it can control your account
- Keep it private and secret
- Treat it like you would your password

## 🚀 Quick Start

### 1. Get Your User Token

**How to find your Discord User Token:**

**On Desktop:**
1. Open Discord
2. Press `Ctrl + Shift + I` (Windows) or `Cmd + Option + I` (Mac)
3. Go to "Application" tab
4. Find "Local Storage" → "https://discord.com"
5. Look for key: `token`
6. Copy the value (starts with `MzI...`)

**WARNING:** This token is extremely sensitive. Never share it!

### 2. Deploy to Railway

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Create new project → Deploy from GitHub
4. Select your `Discord-Selfbot` repository
5. Railway auto-detects Dockerfile

### 3. Set Environment Variables

In Railway project settings, add:

```
USER_TOKEN=your_discord_user_token_here
DASHBOARD_PASSWORD=your_secure_password
DASHBOARD_URL=https://your-project.up.railway.app
FLASK_ENV=production
```

### 4. Deploy

Railway automatically deploys. Access your dashboard at:
```
https://your-project-name.up.railway.app
```

## 📱 Dashboard Features

### **Dashboard**
- Real-time selfbot status
- Messages sent counter
- Commands executed counter
- Guild count
- Friend count
- Server CPU/Memory usage

### **Bot Control**
- Start/stop selfbot
- Monitor uptime
- Check latency

### **Commands**
- View available selfbot commands
- Search commands
- Command descriptions

### **Send Messages**
- Send messages via selfbot
- Send DMs
- View message history

### **Settings**
- Change command prefix
- Toggle debug mode
- Configure auto-start

### **Logs**
- Real-time bot logs
- Color-coded log levels
- Clear logs

## 🛠️ Built-in Selfbot Commands

Use these with `.` prefix (or custom prefix):

```
.ping              - Check latency
.status            - Show selfbot status
.help              - Show all commands
.echo [text]       - Echo text
.clear [amount]    - Delete your messages
.dm [@user] [msg]  - Send DM to user
.user [@user]      - Get user info
```

## 📱 Mobile Support

Fully responsive design:
- ✅ Desktop (Chrome, Firefox, Safari, Edge)
- ✅ Tablets (iPad, Android)
- ✅ Mobile phones (iPhone, Android)
- ✅ Dark theme (Discord-style)

## 🔐 Security Best Practices

1. **NEVER commit your token to Git**
   - Use environment variables
   - `.env` file is in `.gitignore`

2. **Use a strong dashboard password**
   - Minimum 12 characters
   - Mix uppercase, lowercase, numbers, symbols

3. **Enable Railway security**
   - Use private deployments
   - Only share dashboard URL with trusted people

4. **Keep token updated**
   - Discord recommends changing tokens if compromised
   - Change `USER_TOKEN` if you're worried

5. **Use HTTPS only**
   - Railway provides HTTPS automatically
   - Never access over HTTP

## 📊 How It Works

```
Your Computer/Server
    ↓
[Discord Selfbot (selfbot.py)]
    ↓
[Dashboard Server (dashboard_server.py)] ← Running on Railway
    ↓
[Web Dashboard (HTML/CSS/JS)] ← Accessed from browser
```

**The selfbot:**
- Runs on your machine or Railway
- Connects to Discord with your user account
- Sends stats to dashboard API
- Executes commands

**The dashboard:**
- Displays selfbot stats in real-time
- Lets you control the selfbot remotely
- Shows logs and messages
- Fully web-based (no installation needed)

## 🚀 Local Development

### Install Dependencies

```bash
pip install -r requirements-dashboard.txt
pip install discord.py aiohttp
```

### Create `.env` file

```bash
cp .env.example .env
# Edit .env and add your USER_TOKEN
```

### Run Locally

**Terminal 1 - Selfbot:**
```bash
python selfbot.py
```

**Terminal 2 - Dashboard Server:**
```bash
python dashboard_server.py
```

**Then open browser:**
```
http://localhost:5000
```

## 📝 Logging In

Default password: `admin123`

**Change it immediately!**

Set `DASHBOARD_PASSWORD` environment variable to a secure password.

## 🆘 Troubleshooting

### "Invalid Token" Error
- Check your `USER_TOKEN` is correct
- Token format: starts with `MzI...`
- Get fresh token from Discord

### Selfbot Not Connecting
- Verify token is valid
- Check Railway logs
- Make sure token is for your account

### Dashboard Won't Load
- Check Railway deployment status
- Verify environment variables
- Clear browser cache
- Try different browser

### "Authentication Failed"
- Wrong dashboard password
- Check `DASHBOARD_PASSWORD` in Railway
- Try resetting password

## 📖 Environment Variables

| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `USER_TOKEN` | Yes | `MzI...` | Your Discord user token |
| `DASHBOARD_PASSWORD` | No | `secure123` | Dashboard login password |
| `DASHBOARD_URL` | No | `https://...` | Dashboard public URL |
| `FLASK_ENV` | No | `production` | Flask environment |
| `DASHBOARD_HOST` | No | `0.0.0.0` | Server host |
| `DASHBOARD_PORT` | No | `5000` | Server port |

## ⚡ Tips & Tricks

### Custom Selfbot Commands

Edit `selfbot.py` to add your own commands:

```python
async def cmd_mycmd(self, message, args):
    """My custom command"""
    await self.send_response(message, "Response text")

# In setup_commands():
self.command_tree['mycmd'] = self.cmd_mycmd
```

### Change Command Prefix

In `selfbot.py`:
```python
self.commands_prefix = '!'  # Change from '.' to '!'
```

### Add More Features

The dashboard API is extensible. Add endpoints to `dashboard_server.py`:

```python
@app.route('/api/my-endpoint', methods=['GET'])
@require_auth
def my_endpoint():
    return jsonify({'data': 'value'})
```

Then call from `app.js`:
```javascript
fetch(`${API_URL}/my-endpoint`, {
    headers: { 'Authorization': authToken }
})
```

## 📚 Useful Links

- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [Railway Docs](https://docs.railway.app/)
- [Discord Developer Docs](https://discord.com/developers)

## ⚖️ Legal Notice

Using selfbots may violate Discord's Terms of Service. Use at your own risk.

Discord official statement:
> "User accounts are for people to use, not bots."

Always follow Discord's rules and don't spam or cause trouble.

## 📄 License

GNU General Public License v3.0

---

**Made with ❤️ for Discord automation**
