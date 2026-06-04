// API Configuration
const API_URL = window.location.origin + '/api';
let authToken = null;
let botConnected = false;
let refreshInterval = null;

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
            
            // Close mobile menu
            document.querySelector('.sidebar')?.classList.remove('active');
        });
    });

    // Mobile Menu Toggle
    const menuToggle = document.getElementById('menuToggle');
    menuToggle?.addEventListener('click', () => {
        document.querySelector('.sidebar').classList.toggle('active');
    });

    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
        const sidebar = document.querySelector('.sidebar');
        const menuToggle = document.getElementById('menuToggle');
        if (sidebar && !sidebar.contains(e.target) && !menuToggle.contains(e.target)) {
            sidebar.classList.remove('active');
        }
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
    const passwordHash = btoa(password);
    
    // Test the password with a simple API call
    fetch(`${API_URL}/health`, {
        headers: { 'Authorization': passwordHash }
    })
    .then(r => {
        if (r.status === 401) {
            showNotification('Invalid password', 'error');
            return;
        }
        authToken = passwordHash;
        localStorage.setItem('dashboardAuth', authToken);
        document.getElementById('loginModal').classList.remove('active');
        showMainDashboard();
        showNotification('Login successful!', 'success');
    })
    .catch(err => {
        showNotification('Connection error', 'error');
        console.error('Login error:', err);
    });
}

function logout() {
    if (confirm('Are you sure you want to logout?')) {
        localStorage.removeItem('dashboardAuth');
        authToken = null;
        if (refreshInterval) clearInterval(refreshInterval);
        showLoginModal();
        showNotification('Logged out successfully', 'info');
    }
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
    document.getElementById('pageTitle').textContent = 
        pageName.charAt(0).toUpperCase() + pageName.slice(1);
    
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
        const badge = document.getElementById('statusBadge');
        if (badge) {
            badge.textContent = 'ERROR';
            badge.className = 'status-badge offline';
        }
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
        const commandsList = document.getElementById('commandsList');
        if (commandsList) {
            commandsList.innerHTML = '<p>Failed to load commands</p>';
        }
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
    .catch(err => {
        console.error('Error loading logs:', err);
        const logsList = document.getElementById('logsList');
        if (logsList) {
            logsList.innerHTML = '<p>Failed to load logs</p>';
        }
    });
}

// Bot Control Functions
function startBot() {
    fetch(`${API_URL}/bot/start`, {
        method: 'POST',
        headers: { 'Authorization': authToken }
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            showNotification('Bot starting...', 'info');
            setTimeout(loadBotStatus, 2000);
        } else {
            showNotification(data.error || 'Error starting bot', 'error');
        }
    })
    .catch(err => {
        showNotification('Error starting bot: ' + err.message, 'error');
        console.error('Start bot error:', err);
    });
}

function stopBot() {
    if (confirm('Are you sure you want to stop the bot?')) {
        fetch(`${API_URL}/bot/stop`, {
            method: 'POST',
            headers: { 'Authorization': authToken }
        })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                showNotification('Bot stopping...', 'info');
                setTimeout(loadBotStatus, 2000);
            } else {
                showNotification(data.error || 'Error stopping bot', 'error');
            }
        })
        .catch(err => {
            showNotification('Error stopping bot: ' + err.message, 'error');
            console.error('Stop bot error:', err);
        });
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
        if (data.success) {
            showNotification('Message sent!', 'success');
            document.getElementById('messageForm').reset();
            addMessageToHistory(channelId, messageText);
        } else {
            showNotification(data.error || 'Error sending message', 'error');
        }
    })
    .catch(err => {
        showNotification('Error sending message: ' + err.message, 'error');
        console.error('Send message error:', err);
    });
}

function addMessageToHistory(channelId, message) {
    const historyList = document.getElementById('historyList');
    if (!historyList) return;
    
    const div = document.createElement('div');
    div.className = 'message-item';
    div.innerHTML = `
        <strong>Channel ${channelId}:</strong> ${escapeHtml(message)}
        <div class="message-time">${new Date().toLocaleTimeString()}</div>
    `;
    historyList.insertBefore(div, historyList.firstChild);
    
    // Keep only last 10 messages
    while (historyList.children.length > 10) {
        historyList.removeChild(historyList.lastChild);
    }
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
            prefix: prefix || '.',
            token: token || undefined,
            auto_start: autoStart,
            debug_mode: debugMode
        })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            showNotification('Settings saved!', 'success');
        } else {
            showNotification(data.error || 'Error saving settings', 'error');
        }
    })
    .catch(err => {
        showNotification('Error saving settings: ' + err.message, 'error');
        console.error('Save settings error:', err);
    });
}

// Utility Functions
function filterCommands(query) {
    const items = document.querySelectorAll('.command-item');
    items.forEach(item => {
        const name = item.querySelector('.command-name').textContent.toLowerCase();
        const desc = item.querySelector('.command-desc').textContent.toLowerCase();
        const searchQuery = query.toLowerCase();
        item.style.display = name.includes(searchQuery) || desc.includes(searchQuery) ? 'block' : 'none';
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
            if (data.success) {
                showNotification('Logs cleared!', 'success');
                loadLogs();
            } else {
                showNotification(data.error || 'Error clearing logs', 'error');
            }
        })
        .catch(err => {
            showNotification('Error clearing logs: ' + err.message, 'error');
            console.error('Clear logs error:', err);
        });
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
    const secs = seconds % 60;
    return `${hours}h ${minutes}m ${secs}s`;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    const bgColor = type === 'success' ? '#43b581' : type === 'error' ? '#f04747' : '#7289da';
    
    notification.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 15px 20px;
        background-color: ${bgColor};
        color: white;
        border-radius: 4px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        z-index: 999;
        animation: slideIn 0.3s ease;
        font-size: 14px;
        max-width: 300px;
        word-wrap: break-word;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}

// Auto-refresh data
function startDataRefresh() {
    // Clear any existing interval
    if (refreshInterval) clearInterval(refreshInterval);
    
    // Set new interval
    refreshInterval = setInterval(() => {
        const currentPage = document.querySelector('.page.active')?.id;
        
        // Always refresh these
        loadBotStatus();
        
        if (currentPage === 'dashboard') {
            loadStats();
            loadServerInfo();
        } else if (currentPage === 'status') {
            loadBotStatus();
        } else if (currentPage === 'logs') {
            loadLogs();
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

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (refreshInterval) clearInterval(refreshInterval);
});