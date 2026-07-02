// chat_view.jsx — full RAG + LLM chatbot view
// Renders a chat-style Q&A that calls /chat on the backend.

function ChatView({ date, setDate }) {
  const today = '2026-06-08';
  const [question, setQuestion] = React.useState('');
  const [loading, setLoading] = React.useState(false);
  const [answer, setAnswer] = React.useState(null);
  const [sources, setSources] = React.useState([]);
  const [error, setError] = React.useState(null);

  const EXAMPLES = [
    'Mức lương tối thiểu vùng 1 là bao nhiêu?',
    'Tuổi nghỉ hưu được quy định thế nào?',
    'Thời giờ làm việc tối đa một ngày là bao nhiêu?',
    'Người nước ngoài cần giấy phép lao động không?',
  ];

  const ask = async () => {
    const q = question.trim();
    if (!q) return;
    setLoading(true);
    setAnswer(null);
    setSources([]);
    setError(null);
    const data = await window.fetchChatAnswer(q, date);
    setLoading(false);
    if (data.error) {
      setError(data.error);
    } else {
      setAnswer(data.answer);
      setSources(data.sources || []);
    }
  };

  return (
    <div className="chat-view">
      <div className="search-shell">
        <div className="search-row">
          <div className="search-input-wrap">
            <Icon name="search" size={20} style={{ color: 'var(--text-faint)' }} />
            <input
              className="search-input"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter') ask(); }}
              placeholder="Hỏi bất kỳ câu nào về luật lao động…"
            />
          </div>
          <div className="date-field">
            <label className="date-label">
              <Icon name="calendar" size={13} stroke={1.7} />
              Thời điểm áp dụng
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
          <button className="ask-btn" onClick={ask} disabled={loading}>
            {loading
              ? <><span className="spinner" /> Trợ lý đang soạn…</>
              : <><Icon name="sparkle" size={18} /> Hỏi trợ lý</>}
          </button>
        </div>
      </div>

      <div className="chat-examples">
        <span className="chat-examples-label">Câu hỏi gợi ý</span>
        {EXAMPLES.map((ex, i) => (
          <button key={i} className="chat-chip" onClick={() => setQuestion(ex)}>
            {ex}
          </button>
        ))}
      </div>

      <div className="result-area">
        {loading && (
          <div className="answer-card chat-loading">
            <div className="chat-loading-title">Trợ lý AI đang xử lý…</div>
            <div className="chat-loading-body">
              Đang tìm kiếm các văn bản luật liên quan còn hiệu lực vào ngày {date} và soạn câu trả lời.
              Việc này thường mất từ 10 đến 30 giây.
            </div>
          </div>
        )}

        {!loading && error && (
          <div className="answer-card chat-error">
            <div className="chat-error-title">Không kết nối được với hệ thống</div>
            <div className="chat-error-body">
              Hãy kiểm tra: (1) API đang chạy ở cổng 8000, (2) Ollama đang chạy, (3) PostgreSQL đang bật.
              <br /><span className="chat-error-detail">Chi tiết: {error}</span>
            </div>
          </div>
        )}

        {!loading && answer && (
          <div className="answer-card chat-answer">
            <div className="chat-answer-header">
              <Icon name="sparkle" size={16} />
              <span>Câu trả lời — áp dụng ngày {date}</span>
            </div>
            <div className="chat-answer-body">{answer}</div>

            {sources.length > 0 && (
              <div className="chat-sources">
                <div className="chat-sources-title">Nguồn trích dẫn</div>
                {sources.map((s, i) => (
                  <div key={i} className="chat-source-row">
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
        )}

        {!loading && !answer && !error && (
          <div className="answer-card chat-placeholder">
            Gõ câu hỏi và bấm <strong>Hỏi trợ lý</strong>. Trợ lý AI sẽ đọc các văn bản luật
            còn hiệu lực vào ngày bạn chọn và trả lời bằng ngôn ngữ tự nhiên có trích dẫn.
          </div>
        )}
      </div>
    </div>
  );
}

window.ChatView = ChatView;
