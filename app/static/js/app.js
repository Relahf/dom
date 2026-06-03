// WebSocket чат и основная функциональность приложения

class ApartmentHub {
    constructor() {
        this.token = localStorage.getItem('auth_token');
        this.userId = localStorage.getItem('user_id');
        this.ws = null;
        this.messageSound = new Audio('/static/audio/notification.mp3');
        this.soundEnabled = localStorage.getItem('sound_enabled') !== 'false';
    }

    // Аутентификация
    async login(username, password) {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);
        
        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                const data = await response.json();
                this.token = data.token;
                this.userId = data.user_id;
                localStorage.setItem('auth_token', this.token);
                localStorage.setItem('user_id', this.userId);
                window.location.href = '/';
            } else {
                alert('Ошибка входа');
            }
        } catch (error) {
            console.error('Login error:', error);
            alert('Ошибка подключения');
        }
    }

    async register(username, password, apartment) {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);
        formData.append('apartment', apartment);
        
        try {
            const response = await fetch('/api/auth/register', {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                const data = await response.json();
                this.token = data.token;
                this.userId = data.user_id;
                localStorage.setItem('auth_token', this.token);
                localStorage.setItem('user_id', this.userId);
                window.location.href = '/';
            } else {
                alert('Ошибка регистрации');
            }
        } catch (error) {
            console.error('Register error:', error);
            alert('Ошибка подключения');
        }
    }

    logout() {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_id');
        window.location.href = '/';
    }

    // WebSocket чат
    connectChat() {
        if (!this.token) {
            alert('Требуется аутентификация');
            return;
        }

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/chat?token=${this.token}`;

        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            console.log('WebSocket подключен');
            this.loadMessages();
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'message') {
                this.addMessageToChat(data);
                
                // Воспроизведение звука если вкладка не в фокусе
                if (!document.hasFocus() && this.soundEnabled) {
                    this.messageSound.play().catch(() => {});
                }
            }
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        this.ws.onclose = () => {
            console.log('WebSocket отключен');
            setTimeout(() => this.connectChat(), 3000);
        };
    }

    async loadMessages() {
        try {
            const response = await fetch('/api/chat/messages', {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });
            
            if (response.ok) {
                const messages = await response.json();
                const chatContainer = document.getElementById('chat-messages');
                if (chatContainer) {
                    chatContainer.innerHTML = '';
                    messages.forEach(msg => this.addMessageToChat(msg));
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                }
            }
        } catch (error) {
            console.error('Load messages error:', error);
        }
    }

    addMessageToChat(message) {
        const chatContainer = document.getElementById('chat-messages');
        if (!chatContainer) return;

        const msgElement = document.createElement('div');
        msgElement.className = 'chat-message';
        msgElement.innerHTML = `
            <strong>${message.username}</strong>
            ${message.apartment ? `<span class="apartment">кв. ${message.apartment}</span>` : ''}
            <span class="time">${new Date(message.time).toLocaleTimeString('ru-RU')}</span>
            <div>${this.escapeHtml(message.content)}</div>
            ${message.emoji ? `<span>${message.emoji}</span>` : ''}
        `;
        
        chatContainer.appendChild(msgElement);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    sendMessage(content) {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
            alert('Чат не подключен');
            return;
        }

        this.ws.send(JSON.stringify({
            content: content,
            type: 'message'
        }));
    }

    // Управление файлами
    async uploadFile(file, description = '') {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('description', description);

        try {
            const response = await fetch('/api/files/upload', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`
                },
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                alert('Файл загружен успешно');
                return data;
            } else {
                alert('Ошибка загрузки файла');
            }
        } catch (error) {
            console.error('Upload error:', error);
            alert('Ошибка подключения');
        }
    }

    async loadFiles() {
        try {
            const response = await fetch('/api/files', {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (response.ok) {
                const files = await response.json();
                const fileList = document.getElementById('file-list');
                if (fileList) {
                    fileList.innerHTML = '';
                    files.forEach(file => {
                        const li = document.createElement('li');
                        li.className = 'file-item';
                        li.innerHTML = `
                            <div class="file-info">
                                <div class="file-name">${this.escapeHtml(file.name)}</div>
                                <div class="file-meta">${(file.size / 1024 / 1024).toFixed(2)} MB</div>
                            </div>
                            <a href="/api/files/${file.id}/download" class="btn btn-small btn-primary">Скачать</a>
                        `;
                        fileList.appendChild(li);
                    });
                }
            }
        } catch (error) {
            console.error('Load files error:', error);
        }
    }

    // Утилиты
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    toggleSound() {
        this.soundEnabled = !this.soundEnabled;
        localStorage.setItem('sound_enabled', this.soundEnabled);
        const button = document.getElementById('sound-toggle');
        if (button) {
            button.textContent = this.soundEnabled ? '🔔 Звук вкл' : '🔕 Звук выкл';
        }
    }
}

// Глобальный объект приложения
window.hub = new ApartmentHub();

// Инициализация при загрузке
document.addEventListener('DOMContentLoaded', () => {
    // Проверка аутентификации
    if (window.hub.token && window.location.pathname !== '/auth/login' && window.location.pathname !== '/auth/register') {
        window.hub.connectChat();
    }
});
