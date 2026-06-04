# Discord Selfbot Dashboard - Railway Edition

A complete web-based dashboard for controlling your Discord selfbot hosted on Railway.

## 🚀 Quick Start with Railway

### Step 1: Create a Railway Account
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Create a new project

### Step 2: Deploy from GitHub
1. Click "New Project" → "Deploy from GitHub repo"
2. Select your `Discord-Selfbot` repository
3. Railway will auto-detect the Dockerfile and deploy

### Step 3: Set Environment Variables
In Railway project settings, add:

```
DISCORD_TOKEN=your_discord_token_here
DASHBOARD_PASSWORD=your_secure_password
DASHBOARD_HOST=0.0.0.0
DASHBOARD_PORT=5000
FLASK_ENV=production
```

### Step 4: Deploy
Railway will automatically deploy your app. Your dashboard will be available at:
```
https://your-project-name.up.railway.app
```

## 📋 Features

✅ **Dashboard Overview**
- Real-time bot status
- Statistics (messages, commands, guilds)
- Server resources (CPU, memory)

✅ **Bot Control**
- Start/stop bot remotely
- Monitor uptime & latency

✅ **Command Management**
- View all commands
- Search & filter

✅ **Messaging**
- Send messages via bot
- Message history

✅ **Settings**
- Configure prefix
- Update token
- Debug mode

✅ **Logging**
- Real-time logs
- Color-coded levels
- Clear logs

✅ **Mobile Responsive**
- Works on all devices
- Dark theme (Discord-style)

## 🔐 Security

### Important:
1. **Change default password immediately**
2. **Keep bot token secure** - never share it
3. **Use strong passwords** (12+ characters)
4. **Enable HTTPS** (Railway does this automatically)

## 🛠️ Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DISCORD_TOKEN` | Yes | - | Your Discord bot token |
| `DASHBOARD_PASSWORD` | No | admin123 | Dashboard login password |
| `DASHBOARD_HOST` | No | 0.0.0.0 | Server host |
| `DASHBOARD_PORT` | No | 5000 | Server port |
| `FLASK_ENV` | No | production | Flask environment |

## 📱 Mobile Support

The dashboard is fully responsive:
- ✅ Desktop (Chrome, Firefox, Safari, Edge)
- ✅ Tablets (iPad, Android)
- ✅ Mobile phones (iPhone, Android)

## 🔗 API Endpoints

### Bot Status
```
GET  /api/bot/status        - Get bot status
POST /api/bot/start         - Start bot
POST /api/bot/stop          - Stop bot
```

### Statistics
```
GET  /api/bot/stats         - Get bot stats
POST /api/bot/stats         - Update bot stats
GET  /api/server/info       - Get server info
```

### Management
```
GET  /api/bot/commands      - Get commands
POST /api/bot/send-message  - Send message
GET  /api/bot/settings      - Get settings
POST /api/bot/settings      - Save settings
```

### Logs
```
GET  /api/bot/logs          - Get logs
POST /api/bot/logs/clear    - Clear logs
```

### Health
```
GET  /api/health            - Health check
```

## 🐛 Troubleshooting

### Dashboard won't load
1. Check Railway deployment status
2. Verify environment variables are set
3. Check project logs in Railway dashboard

### Can't login
1. Check `DASHBOARD_PASSWORD` environment variable
2. Try refreshing the page
3. Clear browser cache

### Bot won't start
1. Verify `DISCORD_TOKEN` is set correctly
2. Check bot file path in `dashboard_server.py`
3. Check Railway logs for errors

### CORS errors
1. Railway handles CORS automatically
2. Try clearing browser cache
3. Try a different browser

## 📝 Connecting Your Selfbot

To integrate with discord.py selfbot:

```python
import aiohttp

class DashboardClient:
    def __init__(self, bot, dashboard_url):
        self.bot = bot
        self.dashboard_url = dashboard_url
    
    async def update_stats(self):
        stats = {
            'messages_sent': self.bot.messages_sent,
            'commands_executed': self.bot.commands_executed,
            'guild_count': len(self.bot.guilds),
            'friend_count': len(self.bot.friends)
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.dashboard_url}/api/bot/stats",
                json=stats
            ) as resp:
                return await resp.json()
```

## 🚢 Deployment Tips

### Auto-redeploy on Push
Railway automatically redeploys when you push to GitHub. Just:
1. Make changes
2. Git push to your repository
3. Railway redeploys automatically

### Scaling
Railway automatically handles traffic. For high load:
1. Go to Railway project settings
2. Increase "Memory" and "vCPU" as needed
3. Changes apply immediately

### Monitoring
In Railway dashboard:
- View real-time logs
- Monitor CPU/memory usage
- Check deployment status
- View network activity

## 📞 Support

For issues:
1. Check the [troubleshooting](#-troubleshooting) section
2. View logs in Railway dashboard
3. Open an issue on GitHub

## 📄 License

GNU General Public License v3.0

---

**Happy botting!** 🤖
