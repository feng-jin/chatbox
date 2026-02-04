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

function normalizeIso(isoString) {
  if (!isoString) return '';
  // Some browsers are strict with microseconds (>3 digits).
  return String(isoString).replace(/(\.\d{3})\d+/, '$1');
}

function formatCreatedAt(isoString) {
  const d = new Date(normalizeIso(isoString));
  if (Number.isNaN(d.getTime())) return '';
  return d.toLocaleString('zh-CN', {
    month: 'numeric',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function isUuidLike(text) {
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(text);
}

function getDisplayTitle(session) {
  const rawTitle = (session.title || '').trim();
  if (rawTitle && !isUuidLike(rawTitle)) return rawTitle;
  const timeText = formatCreatedAt(session.created_at) || formatCreatedAt(session.updated_at);
  return timeText ? `会话 ${timeText}` : '未命名会话';
}

async function loadSessions() {
  const data = await api('/api/sessions');
  const ul = document.getElementById('sessionList');
  ul.innerHTML = '';
  (data.items || []).forEach(s => {
    const displayTitle = getDisplayTitle(s);
    const li = document.createElement('li');
    li.dataset.sessionId = s.session_id;
    if (s.session_id === currentSessionId) li.classList.add('active');
    const span = document.createElement('span');
    span.className = 'session-label';
    span.textContent = displayTitle;
    const delBtn = document.createElement('button');
    delBtn.type = 'button';
    delBtn.className = 'btn-delete-session';
    delBtn.title = '删除会话';
    delBtn.textContent = '×';
    delBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      deleteSession(s.session_id);
    });
    li.appendChild(span);
    li.appendChild(delBtn);
    li.addEventListener('click', () => selectSession(s.session_id, displayTitle));
    ul.appendChild(li);
  });
}

async function deleteSession(sessionId) {
  if (!confirm('确定要删除该会话吗？')) return;
  try {
    await api(`/api/sessions/${encodeURIComponent(sessionId)}`, { method: 'DELETE' });
    if (currentSessionId === sessionId) {
      currentSessionId = null;
      document.getElementById('sessionTitle').textContent = '选择或新建会话';
      document.getElementById('messages').innerHTML = '';
    }
    await loadSessions();
  } catch (err) {
    alert('删除失败: ' + err.message);
  }
}

function selectSession(sessionId, title) {
  currentSessionId = sessionId;
  document.getElementById('sessionTitle').textContent = title || '未命名会话';
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

function appendUserBubble(container, content) {
  const div = document.createElement('div');
  div.className = 'msg user';
  div.innerHTML = `<div class="role">user</div><div class="content">${escapeHtml(content)}</div>`;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

function appendLoadingBubble(container) {
  const div = document.createElement('div');
  div.className = 'msg assistant loading';
  div.dataset.loading = '1';
  div.innerHTML = `<div class="role">assistant</div><div class="content"><span class="loading-dots"><span>.</span><span>.</span><span>.</span></span></div>`;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
  return div;
}

function appendAssistantBubbleWithTyping(container, fullText, onComplete) {
  const div = document.createElement('div');
  div.className = 'msg assistant';
  div.innerHTML = '<div class="role">assistant</div><div class="content"></div>';
  const contentEl = div.querySelector('.content');
  container.appendChild(div);
  const TYPING_INTERVAL = 25;
  let index = 0;
  function tick() {
    if (index >= fullText.length) {
      if (onComplete) onComplete();
      return;
    }
    index += 1;
    contentEl.textContent = fullText.slice(0, index);
    container.scrollTop = container.scrollHeight;
    setTimeout(tick, TYPING_INTERVAL);
  }
  setTimeout(tick, TYPING_INTERVAL);
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
  selectSession(data.session_id, getDisplayTitle(data));
});

document.getElementById('chatForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const input = document.getElementById('messageInput');
  const message = input.value?.trim();
  if (!message || !currentSessionId) return;
  input.value = '';
  const useRag = document.getElementById('useRag').checked;
  const container = document.getElementById('messages');

  appendUserBubble(container, message);
  const loadingEl = appendLoadingBubble(container);

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
    loadingEl.remove();
    appendAssistantBubbleWithTyping(container, data.assistant_message || '', () => {
      loadSessions().then(() => {
        const activeLi = document.querySelector(`#sessionList li[data-session-id="${currentSessionId}"]`);
        if (activeLi) {
          const label = activeLi.querySelector('.session-label');
          if (label) document.getElementById('sessionTitle').textContent = label.textContent || '未命名会话';
        }
      });
    });
  } catch (err) {
    loadingEl.remove();
    const div = document.createElement('div');
    div.className = 'msg';
    div.innerHTML = `<div class="role">error</div><div class="content">${escapeHtml(err.message)}</div>`;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
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
