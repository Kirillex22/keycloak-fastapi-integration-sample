document.addEventListener('DOMContentLoaded', () => {
    const createForm = document.getElementById('create-post-form');
    const createResult = document.getElementById('create-post-result');
    const getForm = document.getElementById('get-post-form');
    const postOutput = document.getElementById('post-output');
    const deleteBtn = document.getElementById('btn-delete-post');
    const loadProfileBtn = document.getElementById('btn-load-my-profile');
    const profileCard = document.querySelector('.profile-card');

    function showMessage(el, text, isError = false) {
        if (!el) return;
        el.textContent = text;
        el.style.color = isError ? 'tomato' : '';
    }

    // Escape HTML to avoid injection in rendered cards
    function escapeHtml(str) {
        return String(str || '').replace(/[&<>"']/g, function (s) {
            return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[s];
        });
    }

    // Render a post card element
    function renderPostCard(post) {
        const el = document.createElement('article');
        el.className = 'post-card';
        el.dataset.postId = post.id;
        el.innerHTML = `
            <h3>${escapeHtml(post.title)}</h3>
            <p class="muted">ID: ${escapeHtml(post.id)} • Автор: ${escapeHtml(post.owner_id)}</p>
            <div class="post-body">${escapeHtml(post.content)}</div>
            <div class="post-actions"><button class="btn small" data-delete-id="${escapeHtml(post.id)}">Удалить</button></div>
        `;

        const delBtn = el.querySelector('button[data-delete-id]');
        if (delBtn) {
            delBtn.addEventListener('click', async () => {
                if (!confirm('Удалить пост?')) return;
                const pid = delBtn.getAttribute('data-delete-id');
                try {
                    const res = await fetch(`/api/posts/${encodeURIComponent(pid)}`, { method: 'DELETE', credentials: 'include' });
                    const data = await res.json();
                    if (!res.ok) {
                        alert(data.detail || JSON.stringify(data));
                        return;
                    }
                    el.remove();
                } catch (err) {
                    alert('Ошибка: ' + err.message);
                }
            });
        }
        return el;
    }

    if (createForm) {
        createForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const form = new FormData(createForm);
            const body = {
                title: form.get('title'),
                content: form.get('content'),
                owner_id: profileCard ? profileCard.dataset.userId : undefined
            };
            showMessage(createResult, 'Отправка...');
            try {
                const res = await fetch('/api/posts/create', {
                    method: 'POST',
                    credentials: 'include',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(body)
                });
                const data = await res.json();
                if (!res.ok) {
                    // Handle validation (422) with detailed messages
                    if (res.status === 422 && Array.isArray(data.detail)) {
                        const msgs = data.detail.map(d => d.msg ? `${d.loc.join('.')}: ${d.msg}` : JSON.stringify(d)).join('\n');
                        showMessage(createResult, msgs, true);
                    } else {
                        showMessage(createResult, data.detail || JSON.stringify(data), true);
                    }
                    return;
                }
                showMessage(createResult, 'Пост создан: ' + (data.id || '—'));
                // render created post card
                const list = document.getElementById('my-posts');
                if (list) {
                    const postEl = renderPostCard(data);
                    list.prepend(postEl);
                }
                postOutput.textContent = JSON.stringify(data, null, 2);
                createForm.reset();
            } catch (err) {
                showMessage(createResult, 'Ошибка: ' + err.message, true);
            }
        });
    }

    if (getForm) {
        getForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const form = new FormData(getForm);
            const id = form.get('post_id');
            if (!id) return;
            postOutput.textContent = 'Загрузка...';
            try {
                const res = await fetch(`/api/posts/${encodeURIComponent(id)}`, { credentials: 'include' });
                if (res.status === 404) {
                    postOutput.textContent = 'Пост не найден';
                    return;
                }
                const data = await res.json();
                if (!res.ok) {
                    postOutput.textContent = data.detail || JSON.stringify(data);
                    return;
                }
                // render returned post as card and prepend to list
                const list = document.getElementById('my-posts');
                if (list) {
                    const postEl = renderPostCard(data);
                    list.prepend(postEl);
                    postOutput.textContent = '';
                } else {
                    postOutput.textContent = JSON.stringify(data, null, 2);
                }
            } catch (err) {
                postOutput.textContent = 'Ошибка: ' + err.message;
            }
        });

        deleteBtn.addEventListener('click', async () => {
            const idField = getForm.querySelector('input[name="post_id"]');
            const id = idField && idField.value;
            if (!id) return alert('Укажите ID поста');
            if (!confirm('Удалить пост ' + id + '?')) return;
            try {
                const res = await fetch(`/api/posts/${encodeURIComponent(id)}`, { method: 'DELETE', credentials: 'include' });
                const data = await res.json();
                if (!res.ok) {
                    postOutput.textContent = data.detail || JSON.stringify(data);
                    return;
                }
                // remove card from list if present
                const card = document.querySelector(`.post-card[data-post-id="${id}"]`);
                if (card) card.remove();
                postOutput.textContent = JSON.stringify(data, null, 2);
            } catch (err) {
                postOutput.textContent = 'Ошибка: ' + err.message;
            }
        });
    }

    if (loadProfileBtn && profileCard) {
        loadProfileBtn.addEventListener('click', async () => {
            const userId = profileCard.dataset.userId;
            if (!userId) {
                alert('ID пользователя не обнаружен');
                return;
            }
            postOutput.textContent = 'Загрузка профиля...';
            try {
                const res = await fetch(`/api/users/${encodeURIComponent(userId)}`, { credentials: 'include' });
                const data = await res.json();
                if (!res.ok) {
                    postOutput.textContent = data.detail || JSON.stringify(data);
                    return;
                }
                postOutput.textContent = JSON.stringify(data, null, 2);
            } catch (err) {
                postOutput.textContent = 'Ошибка: ' + err.message;
            }
        });
    }
});