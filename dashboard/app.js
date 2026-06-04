// API Configuration
const API_URL = 'http://localhost:5000/api';
let authToken = null;
let botConnected = false;

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    // Check if user is logged in
    const savedAuth = localStorage.getItem('dashboardAuth');
    if (savedAuth) {
        authToken = savedAuth;
        showMainDashboard();
    } else {
        showLoginModal();
    }

    // Event Listeners
    setupEventListeners();
});

// Setup Event Listeners
function setupEventListeners() {
    // Navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const page = link.dataset.page;
            switchPage(page);
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            link.classList.add('active');
        });
    });

    // Mobile Menu Toggle
    const menuToggle = document.getElementById('menuToggle');
    menuToggle?.addEventListener('click', () => {
        document.querySelector('.sidebar').classList.toggle('active');
    });

    // Login Form
    document.getElementById('loginForm')?.addEventListener('submit', (e) => {
        e.preventDefault();
        const password = document.getElementById('password').value;
        attemptLogin(password);
    });

    // Logout Button
    document.getElementById('logoutBtn')?.addEventListener('click', () => {
        logout();
    });

    // Bot Control Buttons
    document.getElementById('startBtn')?.addEventListener('click', () => startBot());
    document.getElementById('stopBtn')?.addEventListener('click', () => stopBot());

    // Message Form
    document.getElementById('messageForm')?.addEventListener('submit', (e) => {
        e.preventDefault();
        sendMessage();
    });

    // Settings Form
    document.getElementById('settingsForm')?.addEventListener('submit', (e) => {
        e.preventDefault();
        saveSettings();
    });

    // Command Search
    document.getElementById('commandSearch')?.addEventListener('input', (e) => {
        filterCommands(e.target.value);
    });

    // Clear Logs
    document.getElementById('clearLogs')?.addEventListener('click', () => {
        clearLogs();
    });
}

// Authentication
function attemptLogin(password) {
    const defaultPassword = 'admin123'; // Change this to your own password
    
    if (password === defaultPassword) {
        authToken = btoa(password);
        localStorage.setItem('dashboardAuth', authToken);
        document.getElementById('loginModal').classList.remove('active');
        showMainDashboard();
        showNotification('Login successful!', 'success');
    } else {
        showNotification('Invalid password', 'error');
    }
}

function logout() {
    localStorage.removeItem('dashboardAuth');
    authToken = null;
    showLoginModal();
    showNotification('Logged out successfully', 'info');
}

// UI Functions
function showLoginModal() {
    document.getElementById('loginModal').classList.add('active');
    document.querySelector('.main-content').style.display = 'none';
}

function showMainDashboard() {
    document.getElementById('loginModal').classList.remove('active');
    document.querySelector('.main-content').style.display = 'flex';
    loadDashboardData();
    startDataRefresh();
}

function switchPage(pageName) {
    document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));
    document.getElementById(pageName)?.classList.add('active');
    document.getElementById('pageTitle').textContent = pageName.charAt(0).toUpperCase() + pageName.slice(1);
    
    // Load page-specific data
    if (pageName === 'status') loadBotStatus();
    if (pageName === 'commands') loadCommands();
    if (pageName === 'logs') loadLogs();
}

// Data Loading Functions
function loadDashboardData() {
    loadBotStatus();
    loadStats();
    loadServerInfo();
}

function loadBotStatus() {
    fetch(`${API_URL}/bot/status`, {
        headers: { 'Authorization': authToken }
    })
    .then(r => r.json())
    .then(data => {
        botConnected = data.connected;
        const badge = document.getElementById('statusBadge');
        const status = document.getElementById('botStatus');
        const uptime = document.getElementById('botUptime');
        const latency = document.getElementById('botLatency');
        const detailedStatus = document.getElementById('detailedStatus');
        
        if (badge) {
            badge.textContent = data.status?.toUpperCase() || 'OFFLINE';
            badge.className = `status-badge ${data.status || 'offline'}`;
        }
        if (status) status.textContent = data.status?.toUpperCase() || 'Offline';
        if (uptime) uptime.textContent = formatUptime(data.uptime_seconds || 0);
        if (latency) latency.textContent = (data.latency || 0).toFixed(0) + ' ms';
        if (detailedStatus) detailedStatus.textContent = data.status?.toUpperCase() || 'Offline';
        
        updateUserInfo(data);
    })
    .catch(err => {
        console.error('Error loading bot status:', err);
        document.getElementById('statusBadge').textContent = 'ERROR';
    });
}

function loadStats() {
    fetch(`${API_URL}/bot/stats`, {
        headers: { 'Authorization': authToken }
    })
    .then(r => r.json())
    .then(data => {
        const messagesSent = document.getElementById('messagesSent');
        const commandsExecuted = document.getElementById('commandsExecuted');
        const guildCount = document.getElementById('guildCount');
        const friendCount = document.getElementById('friendCount');
        
        if (messagesSent) messagesSent.textContent = data.messages_sent || 0;
        if (commandsExecuted) commandsExecuted.textContent = data.commands_executed || 0;
        if (guildCount) guildCount.textContent = data.guild_count || 0;
        if (friendCount) friendCount.textContent = data.friend_count || 0;
    })
    .catch(err => console.error('Error loading stats:', err));
}

function loadServerInfo() {
    fetch(`${API_URL}/server/info`, {
        headers: { 'Authorization': authToken }
    })
    .then(r => r.json())
    .then(data => {
        const cpuUsage = document.getElementById('cpuUsage');
        const memUsage = document.getElementById('memUsage');
        const cpuPercent = document.getElementById('cpuPercent');
        const memPercent = document.getElementById('memPercent');
        
        const cpu = data.cpu_percent || 0;
        const mem = data.memory_percent || 0;
        
        if (cpuUsage) cpuUsage.style.width = cpu + '%';
        if (memUsage) memUsage.style.width = mem + '%';
        if (cpuPercent) cpuPercent.textContent = cpu.toFixed(1) + '%';
        if (memPercent) memPercent.textContent = mem.toFixed(1) + '%';
    })
    .catch(err => console.error('Error loading server info:', err));
}

function loadCommands() {
    fetch(`${API_URL}/bot/commands`, {
        headers: { 'Authorization': authToken }
    })
    .then(r => r.json())
    .then(data => {
        const commandsList = document.getElementById('commandsList');
        if (!commandsList) return;
        
        commandsList.innerHTML = '';
        data.commands.forEach(cmd => {
            const div = document.createElement('div');
            div.className = 'command-item';
            div.innerHTML = `
                <div class="command-name">${cmd.name}</div>
                <div class="command-desc">${cmd.description || 'No description'}</div>
            `;
            commandsList.appendChild(div);
        });
    })
    .catch(err => {
        console.error('Error loading commands:', err);
        document.getElementById('commandsList').innerHTML = '<p>Failed to load commands</p>';
    });
}

function loadLogs() {
    fetch(`${API_URL}/bot/logs`, {
        headers: { 'Authorization': authToken }
    })
    .then(r => r.json())
    .then(data => {
        const logsList = document.getElementById('logsList');
        if (!logsList) return;
        
        logsList.innerHTML = '';
        data.logs.forEach(log => {
            const div = document.createElement('div');
            div.className = `log-line log-${log.level.toLowerCase()}`;
            div.textContent = `[${log.timestamp}] [${log.level}] ${log.message}`;
            logsList.appendChild(div);
        });
        logsList.scrollTop = logsList.scrollHeight;
    })
    .catch(err => console.error('Error loading logs:', err));
}

// Bot Control Functions
function startBot() {
    fetch(`${API_URL}/bot/start`, {
        method: 'POST',
        headers: { 'Authorization': authToken }
    })
    .then(r => r.json())
    .then(data => {
        showNotification('Bot starting...', 'info');
        setTimeout(loadBotStatus, 1000);
    })
    .catch(err => showNotification('Error starting bot', 'error'));
}

function stopBot() {
    if (confirm('Are you sure you want to stop the bot?')) {
        fetch(`${API_URL}/bot/stop`, {
            method: 'POST',
            headers: { 'Authorization': authToken }
        })
        .then(r => r.json())
        .then(data => {
            showNotification('Bot stopping...', 'info');
            setTimeout(loadBotStatus, 1000);
        })
        .catch(err => showNotification('Error stopping bot', 'error'));
    }
}

// Message Functions
function sendMessage() {
    const channelId = document.getElementById('channelId').value;
    const messageText = document.getElementById('messageText').value;
    
    if (!channelId || !messageText) {
        showNotification('Please fill in all fields', 'error');
        return;
    }
    
    fetch(`${API_URL}/bot/send-message`, {
        method: 'POST',
        headers: {
            'Authorization': authToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ channel_id: channelId, message: messageText })
    })
    .then(r => r.json())
    .then(data => {
        showNotification('Message sent!', 'success');
        document.getElementById('messageForm').reset();
        addMessageToHistory(channelId, messageText);
    })
    .catch(err => showNotification('Error sending message', 'error'));
}

function addMessageToHistory(channelId, message) {
    const historyList = document.getElementById('historyList');
    if (!historyList) return;
    
    const div = document.createElement('div');
    div.className = 'message-item';
    div.innerHTML = `
        <strong>Channel ${channelId}:</strong> ${message}
        <div class="message-time">${new Date().toLocaleTimeString()}</div>
    `;
    historyList.insertBefore(div, historyList.firstChild);
}

// Settings Functions
function saveSettings() {
    const prefix = document.getElementById('prefix').value;
    const token = document.getElementById('token').value;
    const autoStart = document.getElementById('autoStart').checked;
    const debugMode = document.getElementById('debugMode').checked;
    
    fetch(`${API_URL}/bot/settings`, {
        method: 'POST',
        headers: {
            'Authorization': authToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            prefix,
            token: token || undefined,
            auto_start: autoStart,
            debug_mode: debugMode
        })
    })
    .then(r => r.json())
    .then(data => showNotification('Settings saved!', 'success'))
    .catch(err => showNotification('Error saving settings', 'error'));
}

// Utility Functions
function filterCommands(query) {
    const items = document.querySelectorAll('.command-item');
    items.forEach(item => {
        const name = item.querySelector('.command-name').textContent.toLowerCase();
        const desc = item.querySelector('.command-desc').textContent.toLowerCase();
        item.style.display = name.includes(query.toLowerCase()) || desc.includes(query.toLowerCase()) ? 'block' : 'none';
    });
}

function clearLogs() {
    if (confirm('Are you sure you want to clear all logs?')) {
        fetch(`${API_URL}/bot/logs/clear`, {
            method: 'POST',
            headers: { 'Authorization': authToken }
        })
        .then(r => r.json())
        .then(data => {
            showNotification('Logs cleared!', 'success');
            loadLogs();
        })
        .catch(err => showNotification('Error clearing logs', 'error'));
    }
}

function updateUserInfo(data) {
    const userInfo = document.getElementById('userInfo');
    if (userInfo) {
        userInfo.textContent = data.bot_name || 'Bot';
    }
    if (document.getElementById('botName')) {
        document.getElementById('botName').textContent = data.bot_name || 'Unknown';
    }
    if (document.getElementById('botId')) {
        document.getElementById('botId').textContent = data.bot_id || 'Unknown';
    }
    if (document.getElementById('connectedSince')) {
        document.getElementById('connectedSince').textContent = data.connected_since || 'Unknown';
    }
}

function formatUptime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 15px 20px;
        background-color: ${type === 'success' ? '#43b581' : type === 'error' ? '#f04747' : '#7289da'};
        color: white;
        border-radius: 4px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        z-index: 999;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Auto-refresh data
function startDataRefresh() {
    setInterval(() => {
        if (botConnected) {
            loadBotStatus();
            loadStats();
            loadServerInfo();
        }
    }, 5000); // Refresh every 5 seconds
}

// Add slide animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);