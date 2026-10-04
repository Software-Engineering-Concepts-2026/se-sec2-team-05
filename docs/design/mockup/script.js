(function () {
  'use strict';

  const courses = ['All', 'CS101', 'MATH210', 'PSY101', 'ECON201'];

  const state = {
    view: 'home',
    loggedIn: true,
    userMenuOpen: false,
    query: '',
    courseFilter: 'All',
    sort: 'newest',
    selectedNoteId: 1,
    bookmarked: {},
    myRatings: {},
    dragOver: false,
    draftCourse: 'CS101',
    draftTags: ['midterm'],
    authTab: 'login',
    notes: [
      { id: 1, title: 'Midterm Summary — Ch.1-5', course: 'CS101', author: 'J. Lee', rating: 4.2, ratingCount: 32, downloads: 410, tags: ['midterm', 'summary'], daysAgo: 2, mine: false,
        comments: [{ author: 'R. Tan', text: 'this saved my grade 🙏' }, { author: 'A. Kim', text: 'page 4 has a typo' }] },
      { id: 2, title: 'Lecture 4 Notes — Recursion', course: 'CS101', author: 'A. Kim', rating: 4.8, ratingCount: 18, downloads: 210, tags: ['recursion', 'week4'], daysAgo: 5, mine: false, comments: [] },
      { id: 3, title: 'Stats Cheatsheet', course: 'MATH210', author: 'R. Tan', rating: 3.9, ratingCount: 9, downloads: 95, tags: ['cheatsheet'], daysAgo: 9, mine: false, comments: [] },
      { id: 4, title: 'Week 3 Slides Recap', course: 'CS101', author: 'You', rating: 4.8, ratingCount: 15, downloads: 180, tags: ['week3'], daysAgo: 12, mine: true, comments: [] },
      { id: 5, title: 'Cognitive Biases Overview', course: 'PSY101', author: 'M. Ortiz', rating: 4.5, ratingCount: 22, downloads: 260, tags: ['overview', 'exam'], daysAgo: 1, mine: false, comments: [] },
      { id: 6, title: 'Supply & Demand Diagrams', course: 'ECON201', author: 'S. Novak', rating: 4.0, ratingCount: 11, downloads: 140, tags: ['diagrams'], daysAgo: 15, mine: false, comments: [] },
      { id: 7, title: 'Final Review Packet', course: 'CS101', author: 'You', rating: 4.9, ratingCount: 40, downloads: 520, tags: ['final', 'review'], daysAgo: 20, mine: true, comments: [] },
      { id: 8, title: 'Memory & Learning Notes', course: 'PSY101', author: 'K. Das', rating: 4.3, ratingCount: 14, downloads: 170, tags: ['memory'], daysAgo: 4, mine: false, comments: [] }
    ]
  };

  function starsForRating(rating) {
    const filled = Math.round(rating);
    return [0, 1, 2, 3, 4].map((i) => i < filled);
  }

  function daysAgoLabel(d) {
    if (d <= 1) return 'today';
    if (d < 7) return d + ' days ago';
    if (d < 30) return Math.round(d / 7) + 'w ago';
    return Math.round(d / 30) + 'mo ago';
  }

  const starSvg = (filled) =>
    `<svg width="15" height="15" viewBox="0 0 24 24" fill="${filled ? '#c0392b' : 'none'}" stroke="#c0392b" stroke-width="1"><polygon points="12 2 15.09 8.63 22 9.24 16.5 14 18.18 21 12 17.27 5.82 21 7.5 14 2 9.24 8.91 8.63"></polygon></svg>`;

  const starSvgBig = (filled) =>
    `<svg width="24" height="24" viewBox="0 0 24 24" fill="${filled ? '#c0392b' : 'none'}" stroke="#c0392b" stroke-width="1.3"><polygon points="12 2 15.09 8.63 22 9.24 16.5 14 18.18 21 12 17.27 5.82 21 7.5 14 2 9.24 8.91 8.63"></polygon></svg>`;

  function el(id) { return document.getElementById(id); }

  function setView(view) {
    state.view = view;
    state.userMenuOpen = false;
    render();
  }

  function render() {
    renderNav();
    ['home', 'detail', 'upload', 'profile', 'login'].forEach((v) => {
      el('view-' + v).style.display = state.view === v ? '' : 'none';
    });
    if (state.view === 'home') renderHome();
    if (state.view === 'detail') renderDetail();
    if (state.view === 'upload') renderUpload();
    if (state.view === 'profile') renderProfile();
    if (state.view === 'login') renderLogin();
  }

  function renderNav() {
    ['home', 'upload', 'profile'].forEach((v) => {
      el('nav-' + v).classList.toggle('active', state.view === v);
    });
    const auth = el('nav-auth');
    if (state.loggedIn) {
      auth.innerHTML = '<div class="avatar-sm" id="avatar-btn">YU</div>' +
        (state.userMenuOpen ? `<div class="user-menu">
          <div class="user-menu-item" id="menu-profile">My profile</div>
          <div class="user-menu-item danger" id="menu-logout">Log out</div>
        </div>` : '');
      el('avatar-btn').onclick = () => { state.userMenuOpen = !state.userMenuOpen; render(); };
      if (state.userMenuOpen) {
        el('menu-profile').onclick = () => setView('profile');
        el('menu-logout').onclick = () => { state.loggedIn = false; setView('login'); };
      }
    } else {
      auth.innerHTML = '<div class="btn-login-nav" id="login-btn">Log in</div>';
      el('login-btn').onclick = () => setView('login');
    }
  }

  function filteredNotes() {
    return state.notes
      .filter((n) => state.courseFilter === 'All' || n.course === state.courseFilter)
      .filter((n) => {
        if (!state.query.trim()) return true;
        const q = state.query.toLowerCase();
        return n.title.toLowerCase().includes(q) || n.course.toLowerCase().includes(q) || n.tags.some((t) => t.toLowerCase().includes(q));
      })
      .sort((a, b) => (state.sort === 'newest' ? a.daysAgo - b.daysAgo : b.rating - a.rating));
  }

  function renderHome() {
    el('search-input').value = state.query;
    const list = filteredNotes();
    el('result-count').textContent = list.length + ' notes';

    el('chip-row').innerHTML =
      courses.map((c) => `<div class="chip ${state.courseFilter === c ? 'active' : ''}" data-course="${c}">${c}</div>`).join('') +
      '<div class="chip-sep"></div>' +
      `<div class="chip chip-sort" id="sort-toggle">Sort: ${state.sort === 'newest' ? 'Newest' : 'Top rated'}
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#5c5548" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
      </div>`;

    document.querySelectorAll('.chip[data-course]').forEach((chip) => {
      chip.onclick = () => { state.courseFilter = chip.dataset.course; render(); };
    });
    el('sort-toggle').onclick = () => { state.sort = state.sort === 'newest' ? 'top' : 'newest'; render(); };

    el('note-grid').innerHTML = list.map((n) => `
      <div class="note-card" data-id="${n.id}">
        <div class="note-card-top">
          <div class="tag-course">${n.course}</div>
          ${n.mine ? '<div class="mine-badge">your note</div>' : ''}
        </div>
        <div class="note-title">${n.title}</div>
        <div class="note-meta">by ${n.author} · ${daysAgoLabel(n.daysAgo)}</div>
        <div class="note-stars">${starsForRating(n.rating).map(starSvg).join('')}<span class="note-rating-text">${n.rating} · ${n.ratingCount} ratings</span></div>
        <div class="note-tags">${n.tags.map((t) => `<div class="note-tag">${t}</div>`).join('')}</div>
      </div>
    `).join('');

    document.querySelectorAll('.note-card').forEach((card) => {
      card.onclick = () => { state.selectedNoteId = Number(card.dataset.id); setView('detail'); };
    });

    el('no-results').style.display = list.length === 0 ? '' : 'none';
    el('note-grid').style.display = list.length === 0 ? 'none' : '';
    if (list.length === 0) el('no-results-title').textContent = `No notes match "${state.query}"`;

    el('search-input').oninput = (e) => { state.query = e.target.value; render(); };
  }

  function renderDetail() {
    const n = state.notes.find((x) => x.id === state.selectedNoteId) || state.notes[0];
    el('d-course').textContent = n.course;
    el('d-title').textContent = n.title;
    el('d-meta').textContent = `by ${n.author} · ${daysAgoLabel(n.daysAgo)} · ${n.downloads} downloads`;
    el('d-rating').innerHTML = `${n.rating} <span>(${n.ratingCount})</span>`;

    const myRating = state.myRatings[n.id] || 0;
    el('star-input').innerHTML = [1, 2, 3, 4, 5].map((i) => `<span data-star="${i}">${starSvgBig(i <= myRating)}</span>`).join('');
    document.querySelectorAll('#star-input [data-star]').forEach((s) => {
      s.style.cursor = 'pointer';
      s.onclick = () => { state.myRatings[n.id] = Number(s.dataset.star); render(); };
    });

    el('btn-bookmark').classList.toggle('active', !!state.bookmarked[n.id]);
    el('btn-bookmark').onclick = () => { state.bookmarked[n.id] = !state.bookmarked[n.id]; render(); };
    el('btn-download').onclick = () => {};
    el('btn-flag').onclick = () => {};
    el('back-to-browse').onclick = () => setView('home');

    el('comments-title').textContent = `Comments · ${n.comments.length}`;
    el('comments-list').innerHTML = n.comments.map((c) => `<div class="comment-item"><b>${c.author}</b> — ${c.text}</div>`).join('');
    el('comment-input').value = '';
    el('btn-post').onclick = () => {
      const val = el('comment-input').value.trim();
      if (!val) return;
      n.comments.push({ author: 'You', text: val });
      render();
    };
  }

  function renderUpload() {
    el('dropzone-label').textContent = state.dragOver ? 'Drop it!' : 'Drag file here or browse';
    el('dropzone').classList.toggle('dragover', state.dragOver);
    el('dropzone').ondragover = (e) => { e.preventDefault(); state.dragOver = true; render(); };
    el('dropzone').ondragleave = () => { state.dragOver = false; render(); };
    el('dropzone').ondrop = (e) => { e.preventDefault(); state.dragOver = false; render(); };

    const courseSelect = el('upload-course');
    if (!courseSelect.dataset.built) {
      courseSelect.innerHTML = courses.filter((c) => c !== 'All').map((c) => `<option value="${c}">${c}</option>`).join('');
      courseSelect.dataset.built = '1';
    }
    courseSelect.value = state.draftCourse;
    courseSelect.onchange = (e) => { state.draftCourse = e.target.value; };

    el('tag-editor').innerHTML = state.draftTags.map((t, i) => `
      <div class="tag-pill" data-idx="${i}">${t}
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#5c5548" stroke-width="2.5" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
      </div>`).join('') + '<input id="tag-input" class="tag-input" placeholder="+ add tag, press Enter">';

    document.querySelectorAll('#tag-editor .tag-pill').forEach((pill) => {
      pill.querySelector('svg').onclick = () => { state.draftTags.splice(Number(pill.dataset.idx), 1); render(); };
    });
    el('tag-input').onkeydown = (e) => {
      if (e.key === 'Enter' && e.target.value.trim()) {
        e.preventDefault();
        state.draftTags.push(e.target.value.trim());
        render();
      }
    };

    el('btn-cancel-upload').onclick = () => setView('home');
    el('btn-publish').onclick = () => {
      const title = el('upload-title').value.trim();
      if (!title) return;
      const newNote = {
        id: Date.now(), title, course: state.draftCourse, author: 'You',
        rating: 5, ratingCount: 0, downloads: 0, tags: state.draftTags.slice(), daysAgo: 0, mine: true, comments: []
      };
      state.notes.unshift(newNote);
      el('upload-title').value = '';
      el('upload-description').value = '';
      state.draftTags = [];
      setView('home');
    };
  }

  function renderProfile() {
    const mine = state.notes.filter((n) => n.author === 'You');
    el('stat-count').textContent = mine.length;
    el('stat-avg').textContent = mine.length ? (mine.reduce((a, n) => a + n.rating, 0) / mine.length).toFixed(1) : '—';
    el('stat-downloads').textContent = mine.reduce((a, n) => a + n.downloads, 0);

    el('my-uploads').innerHTML = mine.map((n) => `
      <div class="upload-row">
        <div class="upload-row-main" data-id="${n.id}">
          <div class="upload-row-title">${n.title}</div>
          <div class="upload-row-meta">${n.course} · ${n.downloads} downloads</div>
        </div>
        <div class="upload-row-actions">
          <div class="upload-row-rating">★ ${n.rating}</div>
          <div class="upload-row-delete" data-del="${n.id}">Delete</div>
        </div>
      </div>
    `).join('');

    document.querySelectorAll('.upload-row-main').forEach((r) => {
      r.onclick = () => { state.selectedNoteId = Number(r.dataset.id); setView('detail'); };
    });
    document.querySelectorAll('[data-del]').forEach((btn) => {
      btn.onclick = () => {
        state.notes = state.notes.filter((n) => n.id !== Number(btn.dataset.del));
        render();
      };
    });
  }

  function renderLogin() {
    el('tab-login').classList.toggle('active', state.authTab === 'login');
    el('tab-signup').classList.toggle('active', state.authTab === 'signup');
    el('btn-login-submit').textContent = state.authTab === 'login' ? 'Log in' : 'Create account';
    el('tab-login').onclick = () => { state.authTab = 'login'; render(); };
    el('tab-signup').onclick = () => { state.authTab = 'signup'; render(); };
    el('btn-login-submit').onclick = () => { state.loggedIn = true; setView('home'); };
  }

  // Static nav bindings
  el('brand').onclick = () => setView('home');
  el('nav-home').onclick = () => setView('home');
  el('nav-upload').onclick = () => setView('upload');
  el('nav-profile').onclick = () => setView('profile');

  render();
})();
