// api.jsx — bridge to the real backend
// When the backend is running, this fetches a real answer from PostgreSQL.
// If the backend is off, it returns null so the UI can fall back to demo data.

async function fetchRealAnswer(question, dateStr, region = '1') {
  try {
    const res = await fetch('http://localhost:8000/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, date: dateStr, region }),
    });
    if (!res.ok) return null;
    const data = await res.json();
    return data.answer;   // same shape the UI's resolve() returns
  } catch (e) {
    console.warn('Backend not reachable, using demo data:', e);
    return null;
  }
}

window.fetchRealAnswer = fetchRealAnswer;
