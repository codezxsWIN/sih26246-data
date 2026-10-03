/**
 * chatbot.js — Pop-Up Assistant Chatbot for LMI Engine
 * Floating circle FAB + chat window + client-side caching + navigation guidance.
 */

(function () {
  'use strict';

  // Client-side cache helper using sessionStorage
  const CACHE_KEY_PREFIX = 'lmi_chatbot_cache_';
  const CACHE_TTL_MS = 15 * 60 * 1000; // 15 minutes

  function hashString(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      hash = (hash << 5) - hash + str.charCodeAt(i);
      hash |= 0;
    }
    return Math.abs(hash).toString(36);
  }

  function getCachedResponse(query) {
    try {
      const key = CACHE_KEY_PREFIX + hashString(query.trim().toLowerCase());
      const raw = sessionStorage.getItem(key);
      if (!raw) return null;
      const data = JSON.parse(raw);
      if (Date.now() - data.ts > CACHE_TTL_MS) {
        sessionStorage.removeItem(key);
        return null;
      }
      return data.value;
    } catch (e) {
      return null;
    }
  }

  function setCachedResponse(query, value) {
    try {
      const key = CACHE_KEY_PREFIX + hashString(query.trim().toLowerCase());
      sessionStorage.setItem(key, JSON.stringify({ ts: Date.now(), value }));
    } catch (e) {
      // Storage quota exceeded or disabled
    }
  }

  // Format simple markdown-like formatting (**bold**, \n)
  function formatMarkdown(text) {
    if (!text) return '';
    let escaped = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
    
    // Bold
    escaped = escaped.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    // Code blocks / inline mono
    escaped = escaped.replace(/`([^`]+)`/g, '<code style="background:#efefef;padding:1px 4px;font-family:monospace;font-size:12px;">$1</code>');
    // Bullet points
    escaped = escaped.replace(/^\s*[-*]\s+(.*)$/gm, '<li style="margin-left: 14px;">$1</li>');
    // Newlines
    escaped = escaped.replace(/\n/g, '<br>');
    return escaped;
  }

  class ChatBotUI {
    constructor() {
      this.isOpen = false;
      this.isWaiting = false;
      this.init();
    }

    init() {
      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => this.mount());
      } else {
        this.mount();
      }
    }

    mount() {
      let root = document.getElementById('chatbot-root');
      if (!root) {
        root = document.createElement('div');
        root.id = 'chatbot-root';
        document.body.appendChild(root);
      }

      root.innerHTML = `
        <button id="chatbot-fab" class="chatbot-fab" title="Skillcast Assistant Copilot" aria-label="Open Chatbot">
          <svg viewBox="0 0 24 24">
            <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H5.2L4 17.2V4h16v12z"/>
            <circle cx="8" cy="9" r="1.5"/>
            <circle cx="12" cy="9" r="1.5"/>
            <circle cx="16" cy="9" r="1.5"/>
          </svg>
          <span class="chatbot-fab-badge"></span>
        </button>

        <div id="chatbot-panel" class="chatbot-panel" aria-hidden="true">
          <div class="chatbot-header">
            <div class="chatbot-title-group">
              <div class="chatbot-avatar-small">AI</div>
              <div class="chatbot-header-text">
                <span class="chatbot-header-title">Skillcast Assistant</span>
                <span class="chatbot-header-sub">Online • Policy & Labour Copilot</span>
              </div>
            </div>
            <button id="chatbot-close-btn" class="chatbot-close-btn" title="Close chat">&times;</button>
          </div>

          <div id="chatbot-messages" class="chatbot-messages">
            <div class="chatbot-msg chatbot-msg-bot">
              Hello! 👋 I am your <strong>Skillcast Copilot</strong>.<br><br>
              Ask me anything about:
              <ul style="margin-top:4px; margin-bottom:4px; padding-left:14px;">
                <li>Labour demand & supply shortages</li>
                <li>Job seeker guidance & software roles</li>
                <li>Policy interventions (PMKVY, NAPS, ITI)</li>
                <li>Navigating the Skillcast portal</li>
              </ul>
            </div>
          </div>

          <form id="chatbot-form" class="chatbot-footer">
            <input 
              type="text" 
              id="chatbot-input" 
              class="chatbot-input" 
              placeholder="Ask about jobs, demand, policies..." 
              autocomplete="off"
            />
            <button type="submit" id="chatbot-send-btn" class="chatbot-send-btn" title="Send message">
              <svg viewBox="0 0 24 24">
                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
              </svg>
            </button>
          </form>
        </div>
      `;

      this.fabEl = document.getElementById('chatbot-fab');
      this.panelEl = document.getElementById('chatbot-panel');
      this.messagesEl = document.getElementById('chatbot-messages');
      this.inputEl = document.getElementById('chatbot-input');
      this.formEl = document.getElementById('chatbot-form');
      this.closeBtnEl = document.getElementById('chatbot-close-btn');

      this.attachEvents();
    }

    attachEvents() {
      this.fabEl.addEventListener('click', () => this.toggle());
      this.closeBtnEl.addEventListener('click', () => this.close());
      this.formEl.addEventListener('submit', (e) => {
        e.preventDefault();
        this.handleSend();
      });
    }

    toggle() {
      if (this.isOpen) {
        this.close();
      } else {
        this.open();
      }
    }

    open() {
      this.isOpen = true;
      this.panelEl.classList.add('open');
      this.fabEl.classList.add('open');
      this.panelEl.setAttribute('aria-hidden', 'false');
      setTimeout(() => this.inputEl.focus(), 150);
    }

    close() {
      this.isOpen = false;
      this.panelEl.classList.remove('open');
      this.fabEl.classList.remove('open');
      this.panelEl.setAttribute('aria-hidden', 'true');
    }

    scrollToBottom() {
      this.messagesEl.scrollTop = this.messagesEl.scrollHeight;
    }

    appendUserMessage(text) {
      const div = document.createElement('div');
      div.className = 'chatbot-msg chatbot-msg-user';
      div.textContent = text;
      this.messagesEl.appendChild(div);
      this.scrollToBottom();
    }

    appendBotMessage(answer, navHints = [], isBlocked = false) {
      const div = document.createElement('div');
      div.className = `chatbot-msg ${isBlocked ? 'chatbot-msg-blocked' : 'chatbot-msg-bot'}`;
      
      let html = formatMarkdown(answer);

      if (navHints && navHints.length > 0) {
        html += `<div class="chatbot-nav-hints">`;
        navHints.forEach((hint) => {
          const roleAttr = hint.role ? `data-role="${hint.role}"` : '';
          html += `
            <button type="button" class="chatbot-hint-pill" data-route="${hint.route}" ${roleAttr}>
              <svg viewBox="0 0 24 24"><path d="M12 4l-1.41 1.41L16.17 11H4v2h12.17l-5.58 5.59L12 20l8-8z"/></svg>
              ${hint.label}
            </button>
          `;
        });
        html += `</div>`;
      }

      div.innerHTML = html;

      // Attach click listeners to nav pills
      const pills = div.querySelectorAll('.chatbot-hint-pill');
      pills.forEach((pill) => {
        pill.addEventListener('click', async (e) => {
          const btn = e.currentTarget;
          const route = btn.getAttribute('data-route');
          const targetRole = btn.getAttribute('data-role');
          
          if (!route) return;

          const cleanRoute = '/' + route.replace(/^#?\/?/, '');
          const currentRole = window.app && window.app.state ? window.app.state.role : null;

          // If a specific targetRole is required and user role doesn't match or not logged in, auto-switch role
          if (targetRole && currentRole !== targetRole && window.app && window.app.auth) {
            try {
              await window.app.auth.login(targetRole, cleanRoute);
              return;
            } catch (err) {
              console.error('Failed to auto-switch role for route:', err);
            }
          }

          // Otherwise navigate directly
          if (window.Router && typeof window.Router.navigate === 'function') {
            window.Router.navigate(cleanRoute);
          } else {
            window.location.hash = cleanRoute;
          }
        });
      });

      this.messagesEl.appendChild(div);
      this.scrollToBottom();
    }

    showTyping() {
      if (document.getElementById('chatbot-typing')) return;
      const div = document.createElement('div');
      div.id = 'chatbot-typing';
      div.className = 'chatbot-typing';
      div.innerHTML = `
        <div class="chatbot-dot"></div>
        <div class="chatbot-dot"></div>
        <div class="chatbot-dot"></div>
      `;
      this.messagesEl.appendChild(div);
      this.scrollToBottom();
    }

    hideTyping() {
      const el = document.getElementById('chatbot-typing');
      if (el) el.remove();
    }

    async handleSend() {
      const query = this.inputEl.value.trim();
      if (!query || this.isWaiting) return;

      this.inputEl.value = '';
      this.appendUserMessage(query);
      this.isWaiting = true;
      this.showTyping();

      // Check client-side cache first
      const cached = getCachedResponse(query);
      if (cached) {
        this.hideTyping();
        this.isWaiting = false;
        this.appendBotMessage(cached.answer, cached.nav_hints, cached.status === 'blocked');
        return;
      }

      try {
        let resp;
        if (window.API && typeof window.API.chatbotQuery === 'function') {
          resp = await window.API.chatbotQuery(query);
        } else {
          // Fallback direct fetch if window.API not ready
          const res = await fetch('http://localhost:8000/api/copilot/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: query }),
          });
          if (res.status === 429) {
            throw new Error('Rate limit exceeded. Please wait 60 seconds before asking another question.');
          }
          resp = await res.json();
        }

        this.hideTyping();
        this.isWaiting = false;

        const isBlocked = resp.status === 'blocked';
        this.appendBotMessage(resp.answer, resp.nav_hints || [], isBlocked);

        // Cache response
        setCachedResponse(query, resp);
      } catch (err) {
        this.hideTyping();
        this.isWaiting = false;
        const errMsg = err.message || 'Unable to connect to Skillcast backend. Please try again.';
        this.appendBotMessage(`⚠️ ${errMsg}`, [], true);
      }
    }
  }

  // Instantiate ChatBot globally
  window.LMIChatBot = new ChatBotUI();
})();
