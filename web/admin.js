// Admin report review wiring (web/admin.html, Issues #17, #18): loads GET /reports, dismisses
// one report (DELETE /reports/<id>) or deletes the reported note (DELETE /reports/<id>/note).
// The pure parts live in admin-utils.js; this file only touches the DOM and fetch.
(function () {
  const { authHeaders, clearSession, loginUrl } = window.SessionUtils;
  const { groupReports, withoutReport, withoutNote, summaryLine, renderReportGroup, adminErrorMessage } =
    window.AdminUtils;
  const { storage, currentSession, fetchJson } = window.Site;

  const loginPage = loginUrl('/admin.html');
  const session = currentSession();
  if (!session) {
    window.location.replace(loginPage);
    return;
  }

  const byId = (id) => document.getElementById(id);
  const adminError = byId('adminError');
  const adminStatus = byId('adminStatus');
  const reloadButton = byId('reloadReports');
  const reportsSummary = byId('reportsSummary');
  const reportsList = byId('reportsList');
  const removeDialog = byId('removeDialog');
  const removeForm = byId('removeForm');
  const removeNoteTitle = byId('removeNoteTitle');
  const removeError = byId('removeError');

  let groups = [];
  let removing = null;
  let dialogOpener = null;

  function say(el, message) {
    el.textContent = message || '';
    el.hidden = !message;
  }

  function loginAgain() {
    clearSession(storage());
    window.location.replace(loginPage);
  }

  function render() {
    reportsList.innerHTML = groups.map(renderReportGroup).join('');
    say(reportsSummary, summaryLine(groups));
  }

  async function loadReports() {
    reloadButton.disabled = true;
    const result = await fetchJson('/reports', { headers: authHeaders(session) });
    reloadButton.disabled = false;
    if (result.status === 401) {
      loginAgain();
      return;
    }
    if (!result.ok || !result.body || !Array.isArray(result.body.reports)) {
      // 403 = logged in but not an admin. Nothing on this page works then, so say why and stop.
      groups = [];
      reportsList.innerHTML = '';
      say(reportsSummary, '');
      say(adminError, adminErrorMessage(result.status, result.body));
      reloadButton.hidden = result.status === 403;
      return;
    }
    say(adminError, '');
    groups = groupReports(result.body.reports);
    render();
  }

  // ---- Dismiss one report ----

  reportsList.addEventListener('click', async (event) => {
    const dismiss = event.target.closest('[data-dismiss-report]');
    if (dismiss) {
      const id = dismiss.dataset.dismissReport;
      dismiss.disabled = true;
      say(adminStatus, '');
      say(adminError, '');
      const result = await fetchJson(`/reports/${encodeURIComponent(id)}`, {
        method: 'DELETE',
        headers: authHeaders(session),
      });
      if (result.status === 401) {
        loginAgain();
        return;
      }
      // 404 = another admin already handled it, which leaves the same list
      if (!result.ok && result.status !== 404) {
        dismiss.disabled = false;
        say(adminError, adminErrorMessage(result.status, result.body));
        return;
      }
      groups = withoutReport(groups, id);
      render();
      say(adminStatus, 'ยกเลิกรายงานแล้ว โน้ตยังอยู่');
      adminStatus.focus();
      return;
    }

    const remove = event.target.closest('[data-remove-note]');
    if (remove) {
      removing = groups.find((group) => String(group.note.id) === remove.dataset.removeNote);
      if (!removing) return;
      removeNoteTitle.textContent = removing.note.title;
      say(removeError, '');
      say(adminStatus, '');
      say(adminError, '');
      dialogOpener = remove;
      removeDialog.showModal();
    }
  });

  // ---- Delete the reported note ----

  function restoreFocus() {
    if (dialogOpener && dialogOpener.isConnected) dialogOpener.focus({ preventScroll: true });
    dialogOpener = null;
  }

  // Focus goes back right away instead of waiting for the 'close' event, which the browser
  // may deliver late (same as the profile page). The listener still covers Esc.
  function closeDialog() {
    removeDialog.close();
    restoreFocus();
  }

  removeDialog.addEventListener('click', (event) => {
    if (event.target === removeDialog || event.target.closest('[data-close-dialog]')) closeDialog();
  });
  removeDialog.addEventListener('close', restoreFocus);

  removeForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const submit = removeForm.querySelector('[type="submit"]');
    submit.disabled = true;
    // any report of the note works: the service deletes the note that report points at
    const reportId = removing.reports[0].id;
    const result = await fetchJson(`/reports/${encodeURIComponent(reportId)}/note`, {
      method: 'DELETE',
      headers: authHeaders(session),
    });
    submit.disabled = false;
    // nothing typed into this dialog can be lost, so go straight to the login page
    if (result.status === 401) {
      loginAgain();
      return;
    }
    if (!result.ok && result.status !== 404) {
      say(removeError, adminErrorMessage(result.status, result.body));
      return;
    }
    dialogOpener = null;
    closeDialog();
    if (result.status === 404) {
      // the report or the note was handled elsewhere: show what is left on the server
      say(adminStatus, adminErrorMessage(404, { error: 'not_found' }));
      await loadReports();
    } else {
      groups = withoutNote(groups, removing.note.id);
      render();
      say(adminStatus, `ลบโน้ต "${removing.note.title}" แล้ว`);
    }
    adminStatus.focus();
  });

  reloadButton.addEventListener('click', () => {
    say(adminStatus, '');
    loadReports();
  });

  loadReports();
})();
