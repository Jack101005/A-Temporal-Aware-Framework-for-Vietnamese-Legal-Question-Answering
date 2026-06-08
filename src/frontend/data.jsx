// data.jsx — Vietnamese labor-law knowledge base (date-aware)
// Every answer resolves against an "effective date" so the date selector
// genuinely changes what comes back.

const fmtVnd = (n) => n.toLocaleString('vi-VN');

// --- Minimum wage regimes (the star demo: changes with the selected date) ---
const WAGE_REGIMES = [
  {
    from: '2024-07-01', to: null,
    doc: 'Nghị định 74/2024/NĐ-CP',
    regions: { 1: 4960000, 2: 4410000, 3: 3860000, 4: 3450000 },
    hourly: { 1: 23800, 2: 21200, 3: 18600, 4: 16600 },
  },
  {
    from: '2022-07-01', to: '2024-06-30',
    doc: 'Nghị định 38/2022/NĐ-CP',
    regions: { 1: 4680000, 2: 4160000, 3: 3640000, 4: 3250000 },
    hourly: { 1: 22500, 2: 20000, 3: 17500, 4: 15600 },
  },
  {
    from: '2020-01-01', to: '2022-06-30',
    doc: 'Nghị định 90/2019/NĐ-CP',
    regions: { 1: 4420000, 2: 3920000, 3: 3430000, 4: 3070000 },
    hourly: { 1: null, 2: null, 3: null, 4: null },
  },
];

function regimeFor(dateStr) {
  for (const r of WAGE_REGIMES) {
    if (dateStr >= r.from && (r.to === null || dateStr <= r.to)) return r;
  }
  return null; // before earliest known regime
}

// --- Static knowledge entries (don't change across the demo date range) ---
// Each entry: id, keywords (for matching), the question text, and a resolver
// that returns { lede, value, valueLabel, body, regions?, sources, note }.

const ENTRIES = [
  {
    id: 'min-wage',
    icon: 'wage',
    keywords: ['lương tối thiểu', 'luong toi thieu', 'lương vùng', 'mức lương', 'minimum wage', 'vùng 1', 'vung 1', 'lương cơ bản'],
    question: 'Lương tối thiểu vùng 1 hiện tại là bao nhiêu?',
    short: 'Lương tối thiểu vùng',
    dateAware: true,
    resolve(dateStr) {
      const r = regimeFor(dateStr);
      if (!r) {
        return {
          notFound: true,
          lede: 'Tại thời điểm đã chọn, chưa có dữ liệu văn bản trong hệ thống. Vui lòng chọn mốc thời gian từ ngày 01/01/2020 trở đi.',
        };
      }
      const v = r.regions[1];
      const h = r.hourly[1];
      return {
        lede: `Theo ${r.doc}, mức lương tối thiểu vùng I là`,
        value: `${fmtVnd(v)} ₫`,
        valueLabel: '/ tháng' + (h ? `  ·  ${fmtVnd(h)} ₫ / giờ` : ''),
        body: 'Đây là mức sàn áp dụng cho người lao động làm việc theo hợp đồng lao động tại các doanh nghiệp thuộc vùng I. Người sử dụng lao động không được trả thấp hơn mức này.',
        regions: r.regions,
        sources: [
          {
            title: r.doc,
            kind: 'Nghị định',
            subject: 'Quy định mức lương tối thiểu đối với người lao động làm việc theo hợp đồng lao động',
            from: r.from, to: r.to,
          },
          {
            title: 'Bộ luật Lao động (Luật 45/2019/QH14)',
            kind: 'Luật',
            subject: 'Điều 91 — Mức lương tối thiểu',
            from: '2021-01-01', to: null,
          },
        ],
      };
    },
  },
  {
    id: 'overtime',
    icon: 'clock',
    keywords: ['làm thêm', 'lam them', 'tăng ca', 'tang ca', 'overtime', 'giờ làm thêm', 'thêm giờ'],
    question: 'Số giờ làm thêm tối đa trong một tháng là bao nhiêu?',
    short: 'Giờ làm thêm tối đa',
    resolve() {
      return {
        lede: 'Theo Bộ luật Lao động 2019 và Nghị quyết 17/2022/UBTVQH15, số giờ làm thêm tối đa là',
        value: '40 giờ',
        valueLabel: '/ tháng  ·  tối đa 200 giờ / năm (300 giờ trong trường hợp đặc biệt)',
        body: 'Số giờ làm thêm trong ngày không quá 50% số giờ làm việc bình thường. Người sử dụng lao động phải được sự đồng ý của người lao động và bảo đảm tổng số giờ làm thêm không vượt quá giới hạn nêu trên.',
        sources: [
          {
            title: 'Bộ luật Lao động (Luật 45/2019/QH14)',
            kind: 'Luật',
            subject: 'Điều 107 — Làm thêm giờ',
            from: '2021-01-01', to: null,
          },
          {
            title: 'Nghị quyết 17/2022/UBTVQH15',
            kind: 'Nghị quyết',
            subject: 'Về số giờ làm thêm trong 01 năm, 01 tháng của người lao động',
            from: '2022-04-01', to: null,
          },
        ],
      };
    },
  },
  {
    id: 'annual-leave',
    icon: 'calendar',
    keywords: ['nghỉ phép', 'nghi phep', 'phép năm', 'phep nam', 'annual leave', 'ngày nghỉ', 'nghỉ hằng năm'],
    question: 'Người lao động được nghỉ phép năm bao nhiêu ngày?',
    short: 'Nghỉ phép năm',
    resolve() {
      return {
        lede: 'Theo Điều 113 Bộ luật Lao động 2019, người lao động làm đủ 12 tháng được nghỉ hằng năm',
        value: '12 ngày',
        valueLabel: 'làm việc / năm (điều kiện lao động bình thường)',
        body: 'Mức nghỉ là 14 ngày đối với người chưa thành niên, lao động khuyết tật hoặc người làm nghề nặng nhọc, độc hại; và 16 ngày đối với công việc đặc biệt nặng nhọc, độc hại. Cứ đủ 5 năm làm việc cho một người sử dụng lao động thì được cộng thêm 01 ngày (Điều 114).',
        sources: [
          {
            title: 'Bộ luật Lao động (Luật 45/2019/QH14)',
            kind: 'Luật',
            subject: 'Điều 113 & 114 — Nghỉ hằng năm',
            from: '2021-01-01', to: null,
          },
        ],
      };
    },
  },
  {
    id: 'maternity',
    icon: 'heart',
    keywords: ['thai sản', 'thai san', 'nghỉ sinh', 'nghi sinh', 'maternity', 'sinh con', 'thai sãn'],
    question: 'Lao động nữ được nghỉ thai sản trong bao lâu?',
    short: 'Nghỉ thai sản',
    resolve() {
      return {
        lede: 'Theo Điều 34 Luật Bảo hiểm xã hội 2014, lao động nữ sinh con được nghỉ việc hưởng chế độ thai sản',
        value: '06 tháng',
        valueLabel: 'trước và sau khi sinh (nghỉ trước sinh tối đa 02 tháng)',
        body: 'Trường hợp sinh đôi trở lên, từ con thứ hai trở đi, cứ mỗi con người mẹ được nghỉ thêm 01 tháng. Thời gian nghỉ này được giữ nguyên trong Luật Bảo hiểm xã hội 2024 (hiệu lực từ 01/7/2025).',
        sources: [
          {
            title: 'Luật Bảo hiểm xã hội (Luật 58/2014/QH13)',
            kind: 'Luật',
            subject: 'Điều 34 — Thời gian hưởng chế độ khi sinh con',
            from: '2016-01-01', to: '2025-06-30',
          },
          {
            title: 'Luật Bảo hiểm xã hội (Luật 41/2024/QH15)',
            kind: 'Luật',
            subject: 'Điều 53 — Thời gian nghỉ việc hưởng chế độ thai sản',
            from: '2025-07-01', to: null,
          },
        ],
      };
    },
  },
];

function matchEntry(query) {
  if (!query || !query.trim()) return null;
  const q = query.toLowerCase();
  let best = null, bestScore = 0;
  for (const e of ENTRIES) {
    let score = 0;
    for (const kw of e.keywords) {
      if (q.includes(kw.toLowerCase())) score += kw.length;
    }
    if (score > bestScore) { bestScore = score; best = e; }
  }
  return best;
}

Object.assign(window, { ENTRIES, matchEntry, regimeFor, fmtVnd, WAGE_REGIMES });
