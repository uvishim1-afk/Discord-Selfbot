# Discord Selfbot Dashboard

A web-based dashboard for controlling your Discord selfbot. This dashboard provides a clean, mobile-friendly interface to manage your selfbot remotely.

## Features

✅ **Dashboard Overview**
- Real-time bot status monitoring
- Quick statistics (messages sent, commands executed, guilds, friends)
- Server resource usage (CPU, memory)

✅ **Bot Control**
- Start/stop bot from dashboard
- Monitor bot uptime and latency

✅ **Command Management**
- View all available commands
- Search and filter commands

✅ **Messaging**
- Send messages through bot
- View message history

✅ **Settings**
- Configure command prefix
- Update bot token
- Set auto-start options
- Enable debug mode

✅ **Logging**
- Real-time bot logs
- Color-coded log levels
- Clear logs functionality

✅ **Responsive Design**
- Works perfectly on desktop, tablet, and mobile
- Dark theme (Discord-inspired)
- Fast and lightweight

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements-dashboard.txt
```

### 2. Start the Dashboard Server

```bash
python3 dashboard_server.py
```

The server will start on `http://localhost:5000`

### 3. Access the Dashboard

Open your browser and navigate to:
```
http://localhost:5000/dashboard
```

### 4. Login

Default password: `admin123`

**Important:** Change this password immediately!

To change the password, set the environment variable:
```bash
export DASHBOARD_PASSWORD="your_secure_password"
```

## Configuration

### Environment Variables

```bash
# Dashboard password (required)
DASHBOARD_PASSWORD=your_secure_password

# Discord bot token (optional if using selfbot)
DISCORD_TOKEN=your_bot_token

# Server host and port
DASHBOARD_HOST=0.0.0.0
DASHBOARD_PORT=5000
```

### Using with Your Selfbot

The dashboard is designed to work alongside your existing selfbot. To integrate:

1. Make sure your selfbot is running or can be started via the dashboard
2. Update the bot file path in `dashboard_server.py` if needed
3. The dashboard will communicate with your bot via the API endpoints

## API Endpoints

### Bot Status
```
GET /api/bot/status
POST /api/bot/start
POST /api/bot/stop
```

### Statistics
```
GET /api/bot/stats
GET /api/server/info
```

### Commands
```
GET /api/bot/commands
```

### Messaging
```
POST /api/bot/send-message
```

### Settings
```
POST /api/bot/settings
```

### Logs
```
GET /api/bot/logs
POST /api/bot/logs/clear
```

## Connecting to Your Selfbot

To integrate the dashboard with your existing Discord selfbot:

### For discord.py Selfbots

Add this to your selfbot code to connect it with the dashboard API:

```python
import aiohttp

class DashboardIntegration:
    def __init__(self, bot):
        self.bot = bot
        self.api_url = "http://localhost:5000/api"
    
    async def update_stats(self):
        stats = {
            'messages_sent': self.bot.messages_sent,
            'commands_executed': self.bot.commands_executed,
            'guild_count': len(self.bot.guilds),
            'friend_count': len(self.bot.friends)
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_url}/bot/stats",
                json=stats
            ) as resp:
                return await resp.json()
```

## Mobile Support

The dashboard is fully responsive and works on:
- ✅ Desktop (Chrome, Firefox, Safari, Edge)
- ✅ Tablets (iPad, Android tablets)
- ✅ Mobile phones (iPhone, Android)

The sidebar automatically collapses on mobile for better space usage.

## Security Notes

⚠️ **Important Security Tips:**

1. **Change the default password immediately**
2. **Use HTTPS in production** (add SSL certificate)
3. **Keep your bot token secure** - never share it
4. **Use strong passwords** (min 12 characters)
5. **Run behind a reverse proxy** (nginx, Apache) in production
6. **Restrict IP access** if possible
7. **Use environment variables** for sensitive data

## Troubleshooting

### Dashboard won't start
- Make sure port 5000 is not in use
- Check if Flask is installed: `pip install flask flask-cors`

### Can't connect to bot
- Ensure your selfbot is running
- Check the bot file path in `dashboard_server.py`
- Verify the bot token is correct

### CORS errors
- Make sure Flask-CORS is installed
- Check that the API_URL in `app.js` matches your server URL

### Mobile layout issues
- Try refreshing the page
- Clear browser cache
- Test on a different device/browser

## File Structure

```
dashboard/
├── index.html          # Main HTML file
├── styles.css          # Styling
├── app.js              # Frontend JavaScript
└── README.md           # This file

dashboard_server.py     # Flask API server
requirements-dashboard.txt
```

## Advanced Setup

### Running Behind Nginx (Production)

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Docker Support (Optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.10

WORKDIR /app
COPY requirements-dashboard.txt .
RUN pip install -r requirements-dashboard.txt
COPY . .

EXPOSE 5000
CMD ["python", "dashboard_server.py"]
```

Build and run:
```bash
docker build -t selfbot-dashboard .
docker run -p 5000:5000 selfbot-dashboard
```

## Contributing

Feel free to submit issues and enhancement requests!

## License

GNU General Public License v3.0

## Support

For issues and questions, please open an issue on GitHub.
