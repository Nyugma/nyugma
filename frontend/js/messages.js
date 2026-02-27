/**
 * Messaging System
 * Handle conversations and messages between connected users
 */

// Require authentication
if (!requireAuth()) {
    // Will redirect to login if not authenticated
}

class MessagesManager {
    constructor() {
        this.apiBaseUrl = window.AppConfig.getBackendUrl();
        this.currentUser = getCurrentUser();
        this.currentConnectionId = null;
        this.refreshInterval = null;
        
        this.initializeElements();
        this.bindEvents();
        this.loadConversations();
        this.startAutoRefresh();
        
        // Check for connection_id in URL
        const urlParams = new URLSearchParams(window.location.search);
        const connectionId = urlParams.get('connection_id');
        if (connectionId) {
            setTimeout(() => this.openChat(connectionId), 500);
        }
    }

    initializeElements() {
        this.conversationsList = document.getElementById('conversationsList');
        this.chatPanel = document.getElementById('chatPanel');
        this.activeChat = document.getElementById('activeChat');
        this.messagesArea = document.getElementById('messagesArea');
        this.messageForm = document.getElementById('messageForm');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.totalUnread = document.getElementById('totalUnread');
        this.chatUserName = document.getElementById('chatUserName');
        this.chatUserType = document.getElementById('chatUserType');
    }

    bindEvents() {
        // Message form submission
        if (this.messageForm) {
            this.messageForm.addEventListener('submit', (e) => this.sendMessage(e));
        }
        
        // Auto-resize textarea
        if (this.messageInput) {
            this.messageInput.addEventListener('input', () => {
                this.messageInput.style.height = 'auto';
                this.messageInput.style.height = this.messageInput.scrollHeight + 'px';
            });
        }
    }

    async loadConversations() {
        try {
            this.conversationsList.innerHTML = `
                <div class="loading-state">
                    <div class="loading-spinner"></div>
                    <p>Loading conversations...</p>
                </div>
            `;
            
            const response = await authenticatedFetch(`${this.apiBaseUrl}/api/messages/conversations`);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Failed to load conversations');
            }
            
            this.displayConversations(data.conversations);
            this.updateUnreadBadge();
            
        } catch (error) {
            console.error('Error loading conversations:', error);
            this.conversationsList.innerHTML = `
                <div class="empty-state">
                    <p>Failed to load conversations</p>
                    <button onclick="messagesManager.loadConversations()" class="btn btn-primary">Retry</button>
                </div>
            `;
        }
    }

    displayConversations(conversations) {
        if (conversations.length === 0) {
            this.conversationsList.innerHTML = `
                <div class="empty-state">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                    </svg>
                    <p>No conversations yet</p>
                    <small>Connect with helpers to start messaging</small>
                </div>
            `;
            return;
        }
        
        this.conversationsList.innerHTML = '';
        
        conversations.forEach(conv => {
            const item = this.createConversationItem(conv);
            this.conversationsList.appendChild(item);
        });
    }

    createConversationItem(conversation) {
        const div = document.createElement('div');
        div.className = 'conversation-item';
        if (this.currentConnectionId === conversation.connection_id) {
            div.classList.add('active');
        }
        
        const otherUser = conversation.other_user;
        const lastMessage = conversation.last_message;
        const unreadCount = conversation.unread_count;
        
        const timeAgo = lastMessage ? this.getTimeAgo(new Date(lastMessage.created_at)) : '';
        const preview = lastMessage ? 
            (lastMessage.is_mine ? 'You: ' : '') + this.truncate(lastMessage.content, 50) : 
            'No messages yet';
        
        div.innerHTML = `
            <div class="conversation-avatar">
                ${otherUser.full_name.charAt(0).toUpperCase()}
            </div>
            <div class="conversation-info">
                <div class="conversation-header">
                    <h4>${this.escapeHtml(otherUser.full_name)}</h4>
                    ${unreadCount > 0 ? `<span class="unread-count">${unreadCount}</span>` : ''}
                </div>
                <p class="conversation-preview">${this.escapeHtml(preview)}</p>
                ${timeAgo ? `<span class="conversation-time">${timeAgo}</span>` : ''}
            </div>
        `;
        
        div.addEventListener('click', () => this.openChat(conversation.connection_id));
        
        return div;
    }

    async openChat(connectionId) {
        try {
            this.currentConnectionId = connectionId;
            
            // Update active state in conversations list
            document.querySelectorAll('.conversation-item').forEach(item => {
                item.classList.remove('active');
            });
            
            // Show loading
            this.activeChat.style.display = 'block';
            this.chatPanel.querySelector('.empty-chat').style.display = 'none';
            this.messagesArea.innerHTML = '<div class="loading-spinner"></div>';
            
            // Load conversation
            const response = await authenticatedFetch(
                `${this.apiBaseUrl}/api/messages/conversation/${connectionId}`
            );
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Failed to load conversation');
            }
            
            // Determine other user (the one we're chatting with)
            const otherUser = data.connection.requester.user_id === this.currentUser.user_id 
                ? data.connection.helper 
                : data.connection.requester;
            
            // Update chat header
            this.chatUserName.textContent = otherUser.full_name;
            this.chatUserType.textContent = otherUser.user_type === 'helper' ? 'Helper' : 'Seeker';
            this.chatUserType.className = `user-type-badge ${otherUser.user_type}`;
            
            // Display messages
            this.displayMessages(data.messages);
            
            // Refresh conversations list to update unread counts
            this.loadConversations();
            
        } catch (error) {
            console.error('Error opening chat:', error);
            this.messagesArea.innerHTML = `
                <div class="error-message">
                    <p>Failed to load conversation</p>
                    <button onclick="messagesManager.openChat('${connectionId}')" class="btn btn-primary">Retry</button>
                </div>
            `;
        }
    }

    displayMessages(messages) {
        this.messagesArea.innerHTML = '';
        
        if (messages.length === 0) {
            this.messagesArea.innerHTML = `
                <div class="empty-messages">
                    <p>No messages yet. Start the conversation!</p>
                </div>
            `;
            return;
        }
        
        messages.forEach(msg => {
            const messageDiv = this.createMessageElement(msg);
            this.messagesArea.appendChild(messageDiv);
        });
        
        // Scroll to bottom
        this.scrollToBottom();
    }

    createMessageElement(message) {
        const div = document.createElement('div');
        div.className = `message ${message.is_mine ? 'message-mine' : 'message-theirs'}`;
        
        const time = new Date(message.created_at).toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });
        
        div.innerHTML = `
            <div class="message-content">
                ${this.escapeHtml(message.content)}
            </div>
            <div class="message-time">${time}</div>
        `;
        
        return div;
    }

    async sendMessage(e) {
        e.preventDefault();
        
        const content = this.messageInput.value.trim();
        if (!content || !this.currentConnectionId) {
            return;
        }
        
        try {
            this.sendButton.disabled = true;
            
            const response = await authenticatedFetch(`${this.apiBaseUrl}/api/messages`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    connection_id: this.currentConnectionId,
                    content: content
                })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Failed to send message');
            }
            
            // Clear input
            this.messageInput.value = '';
            this.messageInput.style.height = 'auto';
            
            // Reload conversation
            await this.openChat(this.currentConnectionId);
            
        } catch (error) {
            console.error('Error sending message:', error);
            alert('Failed to send message. Please try again.');
        } finally {
            this.sendButton.disabled = false;
            this.messageInput.focus();
        }
    }

    closeChat() {
        this.currentConnectionId = null;
        this.activeChat.style.display = 'none';
        this.chatPanel.querySelector('.empty-chat').style.display = 'flex';
        
        // Remove active state from conversations
        document.querySelectorAll('.conversation-item').forEach(item => {
            item.classList.remove('active');
        });
    }

    async updateUnreadBadge() {
        try {
            const response = await authenticatedFetch(`${this.apiBaseUrl}/api/messages/unread`);
            const data = await response.json();
            
            if (response.ok) {
                const count = data.unread_count;
                this.totalUnread.textContent = count;
                this.totalUnread.style.display = count > 0 ? 'inline-block' : 'none';
            }
        } catch (error) {
            console.error('Error updating unread badge:', error);
        }
    }

    startAutoRefresh() {
        // Refresh conversations every 10 seconds
        this.refreshInterval = setInterval(() => {
            if (this.currentConnectionId) {
                this.openChat(this.currentConnectionId);
            } else {
                this.loadConversations();
            }
        }, 10000);
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
    }

    scrollToBottom() {
        this.messagesArea.scrollTop = this.messagesArea.scrollHeight;
    }

    getTimeAgo(date) {
        const seconds = Math.floor((new Date() - date) / 1000);
        
        if (seconds < 60) return 'Just now';
        if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
        if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
        if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
        
        return date.toLocaleDateString();
    }

    truncate(str, length) {
        return str.length > length ? str.substring(0, length) + '...' : str;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.messagesManager = new MessagesManager();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.messagesManager) {
        window.messagesManager.stopAutoRefresh();
    }
});
