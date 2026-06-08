// components.jsx — presentational components for the Labor Law Assistant

// ---- Icons (functional line icons) ----
function Icon({ name, size = 20, stroke = 1.6, style }) {
  const common = {
    width: size, height: size, viewBox: '0 0 24 24', fill: 'none',
    stroke: 'currentColor', strokeWidth: stroke, strokeLinecap: 'round',
    strokeLinejoin: 'round', style,
  };
  const paths = {
    scale: <g><path d="M12 3v18" /><path d="M7 7h10" /><path d="M7 7l-3 6a3 3 0 0 0 6 0z" /><path d="M17 7l-3 6a3 3 0 0 0 6 0z" /><path d="M8 21h8" /></g>,
    search: <g><circle cx="11" cy="11" r="7" /><path d="m20 20-3.5-3.5" /></g>,
    calendar: <g><rect x="3" y="4.5" width="18" height="16" rx="2.5" /><path d="M3 9h18M8 2.5v4M16 2.5v4" /></g>,
    clock: <g><circle cx="12" cy="12" r="9" /><path d="M12 7.5V12l3 2" /></g>,
    heart: <path d="M12 20.5S3.5 15 3.5 8.8A4.3 4.3 0 0 1 12 6a4.3 4.3 0 0 1 8.5 2.8C20.5 15 12 20.5 12 20.5Z" />,
    wage: <g><circle cx="12" cy="12" r="9" /><path d="M12 7v10M9.5 9.2c0-1.1 1.1-1.7 2.5-1.7s2.5.6 2.5 1.7c0 2.6-5 1.4-5 4 0 1.1 1.1 1.7 2.5 1.7s2.5-.6 2.5-1.7" /></g>,
    doc: <g><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z" /><path d="M14 3v5h5M9 13h6M9 17h6" /></g>,
    shield: <g><path d="M12 2.5 4.5 5.5v6c0 4.7 3.2 8.4 7.5 10 4.3-1.6 7.5-5.3 7.5-10v-6z" /><path d="m9 12 2 2 4-4" /></g>,
    arrow: <g><path d="M5 12h14M13 6l6 6-6 6" /></g>,
    sparkle: <path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z" />,
    info: <g><circle cx="12" cy="12" r="9" /><path d="M12 11v5M12 7.5h.01" /></g>,
    check: <path d="M5 12.5l4.5 4.5L19 7" />,
  };
  return <svg {...common} aria-hidden="true">{paths[name] || null}</svg>;
}

// ---- Document-type badge ----
const KIND_STYLES = {
  'Luật': 'kind-law',
  'Nghị định': 'kind-decree',
  'Thông tư': 'kind-circular',
  'Nghị quyết': 'kind-resolution',
};
function KindBadge({ kind }) {
  return <span className={`kind-badge ${KIND_STYLES[kind] || 'kind-decree'}`}>{kind}</span>;
}

// ---- Date helpers ----
const VN_MONTHS = ['01','02','03','04','05','06','07','08','09','10','11','12'];
function fmtDateVN(iso) {
  if (!iso) return '';
  const [y, m, d] = iso.split('-');
  return `${d}/${m}/${y}`;
}
function effectiveRange(from, to) {
  const start = fmtDateVN(from);
  return to ? `${start} – ${fmtDateVN(to)}` : `Từ ${start} · còn hiệu lực`;
}

// ---- Source card ----
function SourceCard({ src, selectedDate, i }) {
  const active = selectedDate >= src.from && (src.to === null || selectedDate <= src.to);
  return (
    <div className={`source-card ${active ? 'is-active' : 'is-inactive'}`} style={{ '--i': i }}>
      <div className="source-icon"><Icon name="doc" size={18} /></div>
      <div className="source-main">
        <div className="source-top">
          <span className="source-title">{src.title}</span>
          <KindBadge kind={src.kind} />
        </div>
        <p className="source-subject">{src.subject}</p>
        <div className="source-range">
          <Icon name="calendar" size={13} stroke={1.7} />
          <span>{effectiveRange(src.from, src.to)}</span>
          {active && <span className="source-active-pill"><Icon name="check" size={11} stroke={2.2} /> Áp dụng tại thời điểm đã chọn</span>}
        </div>
      </div>
    </div>
  );
}

// ---- Region table (only for min-wage answer) ----
const REGION_LABELS = { 1: 'Vùng I', 2: 'Vùng II', 3: 'Vùng III', 4: 'Vùng IV' };
function RegionTable({ regions }) {
  return (
    <div className="region-grid">
      {[1,2,3,4].map((r) => (
        <div key={r} className={`region-cell ${r === 1 ? 'is-primary' : ''}`}>
          <span className="region-label">{REGION_LABELS[r]}</span>
          <span className="region-val">{window.fmtVnd(regions[r])} ₫</span>
        </div>
      ))}
    </div>
  );
}

Object.assign(window, { Icon, KindBadge, SourceCard, RegionTable, fmtDateVN, effectiveRange });
