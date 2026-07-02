// chat_view.jsx — multi-turn RAG chatbot with conversation bubbles

function ChatView({ date, setDate }) {
  const today = '2026-06-08';
  const [input, setInput] = React.useState('');
  const [loading, setLoading] = React.useState(false);
  // messages: [{role:'user'|'assistant', content, sources?, date?}]
  const [messages, setMessages] = React.useState([]);
  const endRef = React.useRef(null);

  const EXAMPLES = [
    'Mức lương tối thiểu vùng 1 là bao nhiêu?',
    'Tuổi nghỉ hưu được quy định thế nào?',
    'Thời giờ làm việc tối đa một ngày?',
    'Người nước ngoài cần giấy phép lao động không?',
  ];

  // auto-scroll to newest message
  React.useEffect(() => {
    if (endRef.current) endRef.current.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const send = async () => {
    const q = input.trim();
    if (!q || loading) return;

    // add user message to UI immediately
    const userMsg = { role: 'user', content: q, date };
    const newMessages = [...messages, userMsg];
    setMessages(newMessages);
    setInput('');
    setLoading(true);

    // build history for API: strip metadata, only role+content
    const history = messages.map(m => ({ role: m.role, content: m.content }));
    const data = await window.fetchChatAnswer(q, date, history);
    setLoading(false);

    if (data.error) {
      setMessages([...newMessages, {
        role: 'assistant',
        content: 'Xin lỗi, không kết nối được với hệ thống. Chi tiết: ' + data.error,
        error: true
      }]);
    } else {
      setMessages([...newMessages, {
        role: 'assistant',
        content: data.answer || '(không có câu trả lời)',
        sources: data.sources || [],
        date: data.query_date
      }]);
    }
  };

  const clearChat = () => setMessages([]);

  const onKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
  };

  return (
    <div className="chat-view">
      {/* Date + clear header */}
      <div className="chat-header-row">
        <div className="chat-date-field">
          <label className="date-label">
            <Icon name="calendar" size={13} stroke={1.7} />
            Áp dụng luật ngày
          </label>
          <input
            type="date"
            className="date-input"
            value={date}
            max={today}
            min="2018-01-01"
            onChange={(e) => setDate(e.target.value)}
          />
        </div>
        {messages.length > 0 && (
          <button className="chat-clear-btn" onClick={clearChat}>
            Cuộc trò chuyện mới
          </button>
        )}
      </div>

      {/* Conversation */}
      <div className="chat-conversation">
        {messages.length === 0 && (
          <div className="chat-welcome">
            <div className="chat-welcome-title">Chào bạn 👋</div>
            <div className="chat-welcome-body">
              Tôi là trợ lý luật lao động Việt Nam. Bạn có thể hỏi tôi bất kỳ điều gì về
              luật lao động, và có thể hỏi tiếp nhiều câu — tôi sẽ nhớ ngữ cảnh cuộc trò chuyện.
            </div>
            <div className="chat-examples">
              <span className="chat-examples-label">Thử hỏi</span>
              {EXAMPLES.map((ex, i) => (
                <button key={i} className="chat-chip" onClick={() => setInput(ex)}>
                  {ex}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={`chat-msg chat-msg--${m.role}`}>
            <div className="chat-bubble">
              <div className="chat-msg-role">
                {m.role === 'user'
                  ? <><Icon name="search" size={12} stroke={2} /> Bạn{m.date ? ` · ${m.date}` : ''}</>
                  : <><Icon name="sparkle" size={12} stroke={2} /> Trợ lý</>}
              </div>
              <div className={`chat-msg-body ${m.error ? 'is-error' : ''}`}>{m.content}</div>
              {m.sources && m.sources.length > 0 && (
                <div className="chat-msg-sources">
                  <div className="chat-msg-sources-title">Trích dẫn</div>
                  {m.sources.map((s, j) => (
                    <div key={j} className="chat-source-row">
                      <span className="chat-source-tag">{s.document_id}</span>
                      <span className="chat-source-meta">
                        <strong>{s.article}</strong>
                        {s.title ? <> — {s.title}</> : null}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="chat-msg chat-msg--assistant">
            <div className="chat-bubble chat-bubble--typing">
              <div className="chat-msg-role"><Icon name="sparkle" size={12} stroke={2} /> Trợ lý</div>
              <div className="chat-typing"><span></span><span></span><span></span></div>
              <div className="chat-typing-note">Đang tra cứu văn bản và soạn câu trả lời…</div>
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      {/* Input */}
      <div className="chat-input-row">
        <textarea
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={onKey}
          placeholder="Nhắn cho trợ lý… (Enter để gửi, Shift+Enter để xuống dòng)"
          rows={1}
        />
        <button className="ask-btn chat-send-btn" onClick={send} disabled={loading || !input.trim()}>
          {loading
            ? <><span className="spinner" /></>
            : <><Icon name="sparkle" size={18} /> Gửi</>}
        </button>
      </div>
    </div>
  );
}

window.ChatView = ChatView;
