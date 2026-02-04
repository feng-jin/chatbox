const API_BASE = '';

let currentSessionId = null;
let uploadedFileIds = [];

async function api(path, options = {}) {
  const url = path.startsWith('http') ? path : `${API_BASE}${path}`;
  const res = await fetch(url, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...options.headers },
  });
  if (!res.ok) {
    const t = await res.text();
    throw new Error(t || res.statusText);
  }
  const contentType = res.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) return res.json();
  return res.text();
}

async function loadSessions() {
  const data = await api('/api/sessions');
  const ul = document.getElementById('sessionList');
  ul.innerHTML = '';
  (data.items || []).forEach(s => {
    const li = document.createElement('li');
    li.textContent = s.title || s.session_id?.slice(0, 8) || '新会话';
    li.dataset.sessionId = s.session_id;
    if (s.session_id === currentSessionId) li.classList.add('active');
    li.addEventListener('click', () => selectSession(s.session_id, s.title));
    ul.appendChild(li);
  });
}

function selectSession(sessionId, title) {
  currentSessionId = sessionId;
  document.getElementById('sessionTitle').textContent = title || sessionId?.slice(0, 8) || '会话';
  document.querySelectorAll('#sessionList li').forEach(el => {
    el.classList.toggle('active', el.dataset.sessionId === sessionId);
  });
  loadHistory();
}

async function loadHistory() {
  if (!currentSessionId) return;
  const data = await api(`/api/history?session_id=${encodeURIComponent(currentSessionId)}`);
  const container = document.getElementById('messages');
  container.innerHTML = '';
  (data.items || []).forEach(m => {
    const div = document.createElement('div');
    div.className = 'msg ' + m.role;
    div.innerHTML = `<div class="role">${m.role}</div><div class="content">${escapeHtml(m.content)}</div>`;
    container.appendChild(div);
  });
  container.scrollTop = container.scrollHeight;
}

function escapeHtml(s) {
  const div = document.createElement('div');
  div.textContent = s;
  return div.innerHTML;
}

document.getElementById('newSession').addEventListener('click', async () => {
  const data = await api('/api/sessions', { method: 'POST', body: JSON.stringify({ title: '' }) });
  currentSessionId = data.session_id;
  await loadSessions();
  selectSession(data.session_id, data.title);
});

document.getElementById('chatForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const input = document.getElementById('messageInput');
  const message = input.value?.trim();
  if (!message || !currentSessionId) return;
  input.value = '';
  const useRag = document.getElementById('useRag').checked;
  try {
    const data = await api('/api/chat', {
      method: 'POST',
      body: JSON.stringify({
        session_id: currentSessionId,
        message,
        use_rag: useRag,
        file_ids: uploadedFileIds,
      }),
    });
    await loadHistory();
  } catch (err) {
    const container = document.getElementById('messages');
    const div = document.createElement('div');
    div.className = 'msg';
    div.innerHTML = `<div class="role">error</div><div class="content">${escapeHtml(err.message)}</div>`;
    container.appendChild(div);
  }
});

document.getElementById('uploadBtn').addEventListener('click', () => document.getElementById('fileInput').click());
document.getElementById('fileInput').addEventListener('change', async (e) => {
  const file = e.target.files?.[0];
  if (!file) return;
  const status = document.getElementById('uploadStatus');
  status.textContent = '上传中...';
  const form = new FormData();
  form.append('file', file);
  try {
    const res = await fetch(`${API_BASE}/api/files`, { method: 'POST', body: form });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    uploadedFileIds.push(data.file_id);
    status.textContent = `已上传: ${data.filename}`;
  } catch (err) {
    status.textContent = '上传失败: ' + err.message;
  }
  e.target.value = '';
});

loadSessions();
