/**
 * copilot.js - AI Policy Copilot Chat Page
 */
window.CopilotPage = {
  messages: [
    { role: "assistant", text: "Welcome to the AI Policy Copilot. Ask me about labour market shortages, demand forecasts, skill gaps, or policy recommendations.\n\nExample questions:\n• Which skills have the highest shortage in Maharashtra?\n• What occupations are projected to grow in the next 12 months?\n• Where is training capacity insufficient?" }
  ],

  render() {
    const main = Utils.clearMain();
    main.appendChild(Utils.el("h1", { className: "page-title" }, "AI Policy Copilot"));
    main.appendChild(Utils.el("p", { className: "page-subtitle" }, "Natural-language interface to the Labour Market Intelligence Engine."));

    const chatContainer = Utils.el("div", { className: "chat-container" });

    // Messages area
    const messagesArea = Utils.el("div", { className: "chat-messages", id: "chat-messages" });
    chatContainer.appendChild(messagesArea);

    // Input area
    const inputArea = Utils.el("div", { className: "chat-input-area" });
    const input = Utils.el("textarea", {
      className: "chat-input",
      id: "chat-input",
      placeholder: "Ask a policy question...",
      rows: "1"
    });
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); this.send(); }
    });
    const sendBtn = Utils.el("button", { className: "btn btn--primary", id: "chat-send", onClick: () => this.send() }, "Send");
    inputArea.appendChild(input);
    inputArea.appendChild(sendBtn);
    chatContainer.appendChild(inputArea);

    main.appendChild(chatContainer);
    this.renderMessages();
  },

  renderMessages() {
    const area = Utils.$("#chat-messages");
    if (!area) return;
    area.innerHTML = "";
    this.messages.forEach(msg => {
      const div = Utils.el("div", { className: `chat-msg chat-msg--${msg.role}` });
      div.appendChild(Utils.el("div", { className: "chat-msg__label" }, msg.role === "user" ? "You" : "AI Copilot"));
      const body = Utils.el("div", { className: "chat-msg__body" });
      body.textContent = msg.text;
      div.appendChild(body);

      // Show grounding facts if present
      if (msg.grounding) {
        const facts = Utils.el("div", { style: { marginTop: "8px", padding: "8px 12px", background: "#f0f9ff", borderRadius: "4px", fontSize: "12px", color: "#1e40af" } });
        facts.innerHTML = "<strong>Grounding:</strong> " + msg.grounding.map(f =>
          `${f.entity} (${f.geography}) — Score: ${f.demand_score}, Risk: ${f.shortage_risk}`
        ).join(" | ");
        div.appendChild(facts);
      }
      if (msg.usedLLM !== undefined) {
        const llmBadge = Utils.el("div", { style: { marginTop: "4px", fontSize: "11px", color: "#64748b" } });
        llmBadge.textContent = msg.usedLLM ? "🟢 Generated with local LLM" : "🔵 Deterministic fallback response";
        div.appendChild(llmBadge);
      }
      area.appendChild(div);
    });
    area.scrollTop = area.scrollHeight;
  },

  async send() {
    const input = Utils.$("#chat-input");
    const sendBtn = Utils.$("#chat-send");
    if (!input || !input.value.trim()) return;

    const query = input.value.trim();
    input.value = "";
    this.messages.push({ role: "user", text: query });
    this.renderMessages();

    sendBtn.disabled = true;
    sendBtn.textContent = "...";

    try {
      const res = await API.queryCopilot(query);
      const result = res.result || {};
      this.messages.push({
        role: "assistant",
        text: result.answer || "No response generated.",
        grounding: result.grounding_facts,
        usedLLM: result.used_llm
      });
    } catch (err) {
      this.messages.push({
        role: "assistant",
        text: "AI Policy Copilot is unavailable. The analytical dashboard remains operational.\n\nError: " + err.message
      });
    }

    sendBtn.disabled = false;
    sendBtn.textContent = "Send";
    this.renderMessages();
  }
};
