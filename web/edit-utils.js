// Pure helpers for the edit-by-token page (web/edit.html, US-19 + US-20 with the edit token
// of ADR-004). They take and return plain values (no DOM, no fetch), so edit-utils.test.js
// runs them under `node --test`. Same loading pattern as search-utils.js: window.EditUtils in
// the browser, module.exports under Node. search-utils.js loads first.
(function (exportTo) {
  const node = typeof module !== 'undefined' && module.exports;
  const { errorMessage } = node ? require('./search-utils.js') : exportTo.SearchUtils;

  // Same header name as services/notes-service/tokens.py (HEADER_NAME).
  const TOKEN_HEADER = 'X-Note-Token';
  const MAX_TOKEN_LENGTH = 200;

  // '' when the typed token can be sent, else the reason. Tokens from POST /notes have no
  // spaces, so a space inside means a bad copy; spaces around it are trimmed away.
  function tokenProblem(value) {
    const token = String(value ?? '').trim();
    if (!token) return 'กรอกรหัสแก้ไขที่ได้ตอนอัปโหลด';
    if (/\s/.test(token)) return 'รหัสต้องไม่มีช่องว่าง ลองคัดลอกใหม่อีกครั้ง';
    if (token.length > MAX_TOKEN_LENGTH) return `รหัสยาวเกิน ${MAX_TOKEN_LENGTH} ตัวอักษร`;
    return '';
  }

  // Only the token header. The page never sends Authorization: notes-service also lets the
  // logged-in owner through (ADR-008), which would make a wrong token look right here.
  function tokenHeaders(token) {
    return { [TOKEN_HEADER]: String(token ?? '').trim() };
  }

  // There is no "check token" endpoint. A PATCH with no fields checks the token first and
  // only then finds nothing to change, so 400 no_fields_to_update means the token is right
  // and nothing was written. 403 = wrong token, 404 = the note is gone.
  function tokenCheckResult(status, body) {
    const code = body && body.error;
    if (status === 400 && code === 'no_fields_to_update') return 'valid';
    if (status === 403) return 'wrong';
    if (status === 404) return 'gone';
    return 'error';
  }

  // Errors of PATCH/DELETE /notes/<id> with a token -> one line for the page.
  function editErrorMessage(status, body) {
    const code = body && body.error;
    if (code === 'forbidden') return 'รหัสแก้ไขไม่ถูกต้อง หรือไม่ใช่รหัสของโน้ตนี้';
    if (code === 'validation_failed') return 'ข้อมูลยังไม่ถูกต้อง แก้ช่องที่มีข้อความสีแดงแล้วลองใหม่';
    if (code === 'no_fields_to_update') return 'ยังไม่ได้แก้ข้อมูลช่องใด';
    return errorMessage(status, body);
  }

  const EditUtils = {
    TOKEN_HEADER,
    MAX_TOKEN_LENGTH,
    tokenProblem,
    tokenHeaders,
    tokenCheckResult,
    editErrorMessage,
  };

  if (node) {
    module.exports = EditUtils;
  } else {
    exportTo.EditUtils = EditUtils;
  }
})(typeof window !== 'undefined' ? window : globalThis);
