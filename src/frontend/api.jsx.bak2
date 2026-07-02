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
    return data.answer;
  } catch (e) {
    console.warn('Backend /ask not reachable, using demo data:', e);
    return null;
  }
}

// NEW: full RAG + LLM chatbot endpoint. Returns { answer, sources, query_date }
// or an { error } object the UI can display.
async function fetchChatAnswer(question, dateStr) {
  try {
    const res = await fetch('http://localhost:8000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, date: dateStr }),
    });
    if (!res.ok) return { error: 'HTTP ' + res.status };
    return await res.json();
  } catch (e) {
    return { error: e.message || 'Không kết nối được với hệ thống.' };
  }
}

window.fetchRealAnswer = fetchRealAnswer;
window.fetchChatAnswer = fetchChatAnswer;
