// app.jsx — stateful App + Tweaks

const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "theme": "trust",
  "accent": "subtle",
  "density": "regular",
  "showRegions": true
}/*EDITMODE-END*/;

function App() {
  const [t, setTweak] = useTweaks(TWEAK_DEFAULTS);
  const today = '2026-06-08';

  const [query, setQuery] = React.useState(window.ENTRIES[0].question);
  const [date, setDate] = React.useState(today);
  const [loading, setLoading] = React.useState(false);
  const [active, setActive] = React.useState(window.ENTRIES[0]); // pre-load min-wage example
  const [result, setResult] = React.useState(window.ENTRIES[0].resolve(today));
  const [flash, setFlash] = React.useState(false);

  const runSearch = React.useCallback((q, d, entryOverride) => {
    const entry = entryOverride || window.matchEntry(q);
    setLoading(true);
    setTimeout(() => {
      if (!entry) {
        setActive(null);
        setResult({ notFound: true, lede: 'Chưa tìm thấy văn bản phù hợp với câu hỏi. Hãy thử một trong các câu hỏi gợi ý bên dưới.' });
      } else {
        setActive(entry);
        setResult(entry.resolve(d));
      }
      setLoading(false);
    }, 820);
  }, []);

  const onSubmit = () => runSearch(query, date);

  const onPick = (entry) => {
    setQuery(entry.question);
    runSearch(entry.question, date, entry);
  };

  // Re-resolve instantly when the effective date changes (the time-travel feature)
  const onDateChange = (d) => {
    setDate(d);
    if (active && !loading) {
      setResult(active.resolve(d));
      setFlash(true);
      setTimeout(() => setFlash(false), 650);
    }
  };

  const showAnswer = active || (result && result.notFound);

  return (
    <div
      className="app"
      data-theme={t.theme}
      data-accent={t.accent}
      data-density={t.density}
    >
      <div className="page">
        <Header />

        <main className="content">
          <div className="hero">
            <h2 className="hero-title">Tra cứu luật lao động <span className="hero-em">như tại bất kỳ thời điểm nào</span></h2>
            <p className="hero-sub">Chọn ngày áp dụng để biết quy định đang có hiệu lực vào đúng mốc thời gian đó — không phải phỏng đoán.</p>
          </div>

          <SearchBar
            query={query} setQuery={setQuery}
            date={date} setDate={onDateChange}
            onSubmit={onSubmit} loading={loading}
          />

          <Suggestions entries={window.ENTRIES} activeId={active && active.id} onPick={onPick} />

          <div className={`result-area ${flash ? 'is-flash' : ''}`}>
            {loading && (
              <div className="answer-card skeleton">
                <div className="sk-line w40" />
                <div className="sk-big" />
                <div className="sk-line w90" />
                <div className="sk-line w75" />
              </div>
            )}
            {!loading && showAnswer && (
              <AnswerCard
                entry={active}
                result={t.showRegions ? result : { ...result, regions: null }}
                date={date}
              />
            )}
          </div>
        </main>

        <footer className="app-foot">
          <Icon name="info" size={13} stroke={1.7} />
          <span>Thông tin mang tính tham khảo, được tổng hợp từ văn bản quy phạm pháp luật. Vui lòng đối chiếu bản gốc khi áp dụng.</span>
        </footer>
      </div>

      <TweaksPanel>
        <TweakSection label="Hướng thiết kế" />
        <TweakRadio
          label="Theme" value={t.theme}
          options={['trust', 'editorial', 'bold']}
          onChange={(v) => setTweak('theme', v)}
        />
        <TweakRadio
          label="Sắc đỏ cờ" value={t.accent}
          options={['subtle', 'off', 'bold']}
          onChange={(v) => setTweak('accent', v)}
        />
        <TweakSection label="Bố cục" />
        <TweakRadio
          label="Mật độ" value={t.density}
          options={['compact', 'regular', 'comfy']}
          onChange={(v) => setTweak('density', v)}
        />
        <TweakToggle
          label="Bảng các vùng" value={t.showRegions}
          onChange={(v) => setTweak('showRegions', v)}
        />
      </TweaksPanel>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
