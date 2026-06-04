#!/usr/bin/env python3
"""
Discord Selfbot with Dashboard Integration
Provides a selfbot that works with the web dashboard
"""

import discord
from discord.ext import commands, tasks
import aiohttp
import os
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Selfbot Configuration
USER_TOKEN = os.getenv('USER_TOKEN')  # Your Discord user token
DASHBOARD_URL = os.getenv('DASHBOARD_URL', 'http://localhost:5000')
DASHBOARD_PASSWORD = os.getenv('DASHBOARD_PASSWORD', 'admin123')

if not USER_TOKEN:
    raise ValueError("USER_TOKEN environment variable not set!")

class SelfbotDashboard(commands.Cog):
    """Cog to handle dashboard integration"""
    
    def __init__(self, client):
        self.client = client
        self.messages_sent = 0
        self.commands_executed = 0
        self.start_time = datetime.now()
        self.sync_stats.start()
    
    @tasks.loop(seconds=10)
    async def sync_stats(self):
        """Send stats to dashboard every 10 seconds"""
        try:
            auth = __import__('base64').b64encode(
                DASHBOARD_PASSWORD.encode()
            ).decode()
            
            stats = {
                'messages_sent': self.messages_sent,
                'commands_executed': self.commands_executed,
                'guild_count': len(self.client.guilds),
                'friend_count': len(self.client.user.relationships) if hasattr(self.client.user, 'relationships') else 0
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{DASHBOARD_URL}/api/bot/stats",
                    json=stats,
                    headers={'Authorization': auth}
                ) as resp:
                    if resp.status == 200:
                        logger.info("Stats synced to dashboard")
        except Exception as e:
            logger.error(f"Error syncing stats: {e}")
    
    @sync_stats.before_loop
    async def before_sync_stats(self):
        """Wait for client to be ready"""
        await self.client.wait_until_ready()

class Selfbot(discord.Client):
    """Custom Discord client for selfbot"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.commands_prefix = '.'
        self.dashboard = None
        self.command_tree = {}
        self.setup_commands()
    
    def setup_commands(self):
        """Setup selfbot commands"""
        self.command_tree = {
            'ping': self.cmd_ping,
            'status': self.cmd_status,
            'clear': self.cmd_clear,
            'dm': self.cmd_dm,
            'help': self.cmd_help,
            'echo': self.cmd_echo,
            'user': self.cmd_user,
        }
    
    async def on_ready(self):
        """Called when selfbot is ready"""
        logger.info(f"Selfbot logged in as {self.user}")
        logger.info(f"User ID: {self.user.id}")
        logger.info(f"Connected to {len(self.guilds)} guilds")
        
        # Add dashboard cog
        if not self.dashboard:
            self.dashboard = SelfbotDashboard(self)
    
    async def on_message(self, message):
        """Handle incoming messages"""
        # Ignore messages from others
        if message.author != self.user:
            return
        
        # Check if message starts with prefix
        if not message.content.startswith(self.commands_prefix):
            return
        
        # Parse command
        content = message.content[len(self.commands_prefix):]
        parts = content.split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        # Execute command
        if command in self.command_tree:
            try:
                await self.command_tree[command](message, args)
                if self.dashboard:
                    self.dashboard.commands_executed += 1
            except Exception as e:
                logger.error(f"Error executing command {command}: {e}")
                await self.send_response(message, f"Error: {str(e)}")
    
    # ============== SELFBOT COMMANDS ==============
    
    async def cmd_ping(self, message, args):
        """Respond with pong"""
        latency = round(self.latency * 1000)
        await self.send_response(message, f"Pong! Latency: {latency}ms")
    
    async def cmd_status(self, message, args):
        """Show selfbot status"""
        uptime = datetime.now() - self.dashboard.start_time if self.dashboard else None
        status_text = (
            f"**Selfbot Status**\n"
            f"User: {self.user}\n"
            f"Guilds: {len(self.guilds)}\n"
            f"Messages Sent: {self.dashboard.messages_sent if self.dashboard else 0}\n"
            f"Commands Executed: {self.dashboard.commands_executed if self.dashboard else 0}\n"
            f"Latency: {round(self.latency * 1000)}ms\n"
            f"Uptime: {str(uptime) if uptime else 'N/A'}"
        )
        await self.send_response(message, status_text)
    
    async def cmd_help(self, message, args):
        """Show available commands"""
        help_text = (
            "**Available Commands:**\n"
            f"{self.commands_prefix}ping - Check latency\n"
            f"{self.commands_prefix}status - Show bot status\n"
            f"{self.commands_prefix}clear [amount] - Clear messages\n"
            f"{self.commands_prefix}dm [@user] [message] - Send DM\n"
            f"{self.commands_prefix}echo [text] - Echo text\n"
            f"{self.commands_prefix}user [@user] - Get user info\n"
            f"{self.commands_prefix}help - Show this message"
        )
        await self.send_response(message, help_text)
    
    async def cmd_echo(self, message, args):
        """Echo the provided text"""
        if not args:
            await self.send_response(message, "Please provide text to echo")
            return
        await self.send_response(message, args)
    
    async def cmd_clear(self, message, args):
        """Clear messages from current channel"""
        try:
            amount = int(args) if args else 10
            if amount > 100:
                amount = 100
            
            deleted = 0
            async for msg in message.channel.history(limit=amount):
                if msg.author == self.user:
                    await msg.delete()
                    deleted += 1
            
            await self.send_response(message, f"Deleted {deleted} messages")
        except ValueError:
            await self.send_response(message, "Invalid number")
        except Exception as e:
            await self.send_response(message, f"Error: {str(e)}")
    
    async def cmd_dm(self, message, args):
        """Send a DM to a user"""
        if not args:
            await self.send_response(message, "Usage: .dm [@user] [message]")
            return
        
        try:
            parts = args.split(maxsplit=1)
            user_mention = parts[0]
            dm_text = parts[1] if len(parts) > 1 else ""
            
            # Extract user ID from mention
            if user_mention.startswith('<@') and user_mention.endswith('>'):
                user_id = int(user_mention[2:-1])
                user = await self.fetch_user(user_id)
                await user.send(dm_text)
                await self.send_response(message, f"DM sent to {user}")
                if self.dashboard:
                    self.dashboard.messages_sent += 1
            else:
                await self.send_response(message, "Invalid user mention")
        except Exception as e:
            await self.send_response(message, f"Error: {str(e)}")
    
    async def cmd_user(self, message, args):
        """Get user information"""
        try:
            if not args:
                user = message.author
            else:
                if args.startswith('<@') and args.endswith('>'):
                    user_id = int(args[2:-1])
                    user = await self.fetch_user(user_id)
                else:
                    await self.send_response(message, "Invalid user mention")
                    return
            
            user_info = (
                f"**User Info:**\n"
                f"Name: {user}\n"
                f"ID: {user.id}\n"
                f"Created: {user.created_at}\n"
                f"Bot: {user.bot}\n"
                f"Avatar: {user.avatar.url if user.avatar else 'None'}"
            )
            await self.send_response(message, user_info)
        except Exception as e:
            await self.send_response(message, f"Error: {str(e)}")
    
    # ============== UTILITY METHODS ==============
    
    async def send_response(self, original_message, response_text):
        """Send response to the message channel"""
        try:
            await original_message.edit(content=response_text)
            if self.dashboard:
                self.dashboard.messages_sent += 1
        except discord.errors.HTTPException:
            # If edit fails, send new message
            try:
                await original_message.channel.send(response_text[:2000])  # Discord limit
                if self.dashboard:
                    self.dashboard.messages_sent += 1
            except Exception as e:
                logger.error(f"Error sending message: {e}")

def main():
    """Start the selfbot"""
    print("""
    ╔════════════════════════════════════════╗
    ║  Discord Selfbot with Dashboard        ║
    ║  Starting...                            ║
    ╚════════════════════════════════════════╝
    """)
    
    # Create selfbot instance
    intents = discord.Intents.all()
    selfbot = Selfbot(intents=intents)
    
    # Start the selfbot
    try:
        selfbot.run(USER_TOKEN)
    except discord.errors.LoginFailure:
        logger.error("Invalid token! Check your USER_TOKEN")
        raise
    except KeyboardInterrupt:
        logger.info("Selfbot shutting down...")

if __name__ == '__main__':
    main()