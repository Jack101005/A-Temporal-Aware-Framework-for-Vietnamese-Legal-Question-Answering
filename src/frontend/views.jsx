// views.jsx — header, search bar, answer card

function Header() {
  return (
    <header className="app-header">
      <div className="brand">
        <div className="brand-mark"><Icon name="scale" size={24} stroke={1.7} /></div>
        <div className="brand-text">
          <h1 className="brand-name">Trợ lý Pháp luật Lao động</h1>
          <p className="brand-tag">Câu trả lời pháp luật chính xác theo thời điểm</p>
        </div>
      </div>
      <div className="header-badge">
        <Icon name="shield" size={15} stroke={1.7} />
        <span>Đối chiếu văn bản gốc</span>
      </div>
    </header>
  );
}

function SearchBar({ query, setQuery, date, setDate, onSubmit, loading }) {
  const today = '2026-06-08';
  return (
    <div className="search-shell">
      <div className="search-row">
        <div className="search-input-wrap">
          <Icon name="search" size={20} style={{ color: 'var(--text-faint)' }} />
          <input
            className="search-input"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter') onSubmit(); }}
            placeholder="Hỏi về luật lao động… (vd: Lương tối thiểu vùng 1 hiện tại là bao nhiêu?)"
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
        <button className="ask-btn" onClick={onSubmit} disabled={loading}>
          {loading
            ? <><span className="spinner" /> Đang tra cứu…</>
            : <><Icon name="sparkle" size={18} /> Tìm câu trả lời</>}
        </button>
      </div>
    </div>
  );
}

function Suggestions({ entries, activeId, onPick }) {
  return (
    <div className="suggestions">
      <span className="suggestions-label">Câu hỏi gợi ý</span>
      <div className="chips">
        {entries.map((e) => (
          <button
            key={e.id}
            className={`chip ${activeId === e.id ? 'is-active' : ''}`}
            onClick={() => onPick(e)}
          >
            <Icon name={e.icon} size={15} stroke={1.7} />
            {e.short}
          </button>
        ))}
      </div>
    </div>
  );
}

function AnswerCard({ entry, result, date }) {
  if (result.notFound) {
    return (
      <div className="answer-card answer-empty">
        <div className="empty-icon"><Icon name="info" size={26} stroke={1.6} /></div>
        <p className="empty-text">{result.lede}</p>
      </div>
    );
  }
  return (
    <div className="answer-block">
      <div className="answer-card">
        <div className="answer-q">
          <Icon name={entry.icon} size={18} stroke={1.7} />
          <span>{entry.question}</span>
        </div>
        <p className="answer-lede">{result.lede}</p>
        <div className="answer-value">
          <span className="value-num">{result.value}</span>
          <span className="value-label">{result.valueLabel}</span>
        </div>
        {result.regions && <RegionTable regions={result.regions} />}
        <p className="answer-body">{result.body}</p>
        <div className="valid-strip">
          <Icon name="check" size={14} stroke={2.1} />
          <span>Câu trả lời có hiệu lực tính đến <strong>{fmtDateVN(date)}</strong></span>
        </div>
      </div>

      <div className="sources">
        <div className="sources-head">
          <Icon name="doc" size={16} stroke={1.7} />
          <h3>Nguồn pháp lý</h3>
          <span className="sources-count">{result.sources.length} văn bản</span>
        </div>
        <div className="sources-list">
          {result.sources.map((s, i) => (
            <SourceCard key={i} src={s} selectedDate={date} i={i} />
          ))}
        </div>
      </div>
    </div>
  );
}

Object.assign(window, { Header, SearchBar, Suggestions, AnswerCard });
