// Pure helpers for the upload page (web/upload.html).
// validateUpload repeats the rules of services/notes-service/validation.py, so the form can
// point at every wrong field before a 20 MB file goes over the network. The service still
// checks everything again; when the two disagree, the service's answer is the one shown.
// Same loading pattern as search-utils.js: window.UploadUtils in the browser, module.exports
// under Node.
(function (exportTo) {
  // Keep in step with REQUIRED_FIELDS, MAX_LENGTHS, ALLOWED_CONTENT_TYPES and MAX_FILE_BYTES
  // in services/notes-service/validation.py.
  const REQUIRED_FIELDS = ['title', 'subject_name', 'subject_code', 'faculty', 'year_level', 'lesson'];
  const OPTIONAL_FIELDS = ['topic', 'class_date', 'description'];
  const MAX_LENGTHS = {
    title: 200,
    subject_name: 200,
    subject_code: 30,
    faculty: 100,
    lesson: 200,
    topic: 200,
  };
  const MIN_YEAR_LEVEL = 1;
  const MAX_YEAR_LEVEL = 8;
  const ALLOWED_CONTENT_TYPES = ['application/pdf', 'image/png', 'image/jpeg'];
  const MAX_FILE_BYTES = 20 * 1024 * 1024;
  const MAX_FILE_MB = MAX_FILE_BYTES / (1024 * 1024);

  function isIsoDate(value) {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
    const parsed = new Date(`${value}T00:00:00Z`);
    // new Date rolls 2026-02-30 over to March, so compare it back to the text
    return !Number.isNaN(parsed.getTime()) && parsed.toISOString().slice(0, 10) === value;
  }

  // fields: {name: string} as read from the form. Returns {field: reason} for the text fields;
  // empty means they can be sent. Every field is checked, so the user fixes them all in one go
  // (the service does the same). Used by the upload form and the profile page's edit form.
  function validateMetadata(fields) {
    const errors = {};
    const value = (name) => String(fields[name] ?? '').trim();

    for (const name of REQUIRED_FIELDS) {
      const text = value(name);
      if (!text) {
        errors[name] = 'จำเป็นต้องกรอก';
      } else if (MAX_LENGTHS[name] && text.length > MAX_LENGTHS[name]) {
        errors[name] = `ยาวเกิน ${MAX_LENGTHS[name]} ตัวอักษร`;
      }
    }

    const year = value('year_level');
    if (year && !errors.year_level) {
      if (!/^\d+$/.test(year)) {
        errors.year_level = 'ต้องเป็นตัวเลข';
      } else if (Number(year) < MIN_YEAR_LEVEL || Number(year) > MAX_YEAR_LEVEL) {
        errors.year_level = `ต้องอยู่ระหว่าง ${MIN_YEAR_LEVEL}-${MAX_YEAR_LEVEL}`;
      }
    }

    const topic = value('topic');
    if (topic.length > MAX_LENGTHS.topic) errors.topic = `ยาวเกิน ${MAX_LENGTHS.topic} ตัวอักษร`;

    const classDate = value('class_date');
    if (classDate && !isIsoDate(classDate)) errors.class_date = 'ต้องเป็นรูปแบบ YYYY-MM-DD';

    return errors;
  }

  // validateMetadata plus the file ({name, size, type} or null).
  function validateUpload(fields, file) {
    const errors = validateMetadata(fields);
    if (!file || !file.name) {
      errors.file = 'ต้องแนบไฟล์โน้ต';
    } else if (!ALLOWED_CONTENT_TYPES.includes(String(file.type).toLowerCase())) {
      errors.file = 'รองรับเฉพาะไฟล์ PDF, PNG และ JPG';
    } else if (!file.size) {
      errors.file = 'ไฟล์ว่าง';
    } else if (file.size > MAX_FILE_BYTES) {
      errors.file = `ไฟล์ใหญ่เกิน ${MAX_FILE_MB} MB`;
    }

    return errors;
  }

  // Form values -> the text fields POST /notes takes. Optional fields left empty are not sent,
  // the same as a form that never had them.
  function uploadFields(fields) {
    const sent = {};
    for (const name of [...REQUIRED_FIELDS, ...OPTIONAL_FIELDS]) {
      const text = String(fields[name] ?? '').trim();
      if (text) sent[name] = text;
    }
    return sent;
  }

  // POST /notes error -> one line for the top of the form. Field-level reasons come from the
  // body's `fields`, the same shape as validateUpload's result.
  function uploadErrorMessage(status, body) {
    const code = body && body.error;
    if (code === 'validation_failed') return 'ข้อมูลยังไม่ถูกต้อง แก้ช่องที่มีข้อความสีแดงแล้วลองใหม่';
    if (code === 'unauthorized') return 'เซสชันหมดอายุหรือออกจากระบบไปแล้ว กรุณาเข้าสู่ระบบใหม่ก่อนอัปโหลด';
    if (code === 'auth_unavailable') return 'ระบบยืนยันตัวตนไม่พร้อมใช้งานตอนนี้ ลองใหม่อีกสักครู่';
    // A body over the gateway's limit is cut off by nginx with an HTML page, so there is no JSON
    if (status === 413) return `ไฟล์ใหญ่เกิน ${MAX_FILE_MB} MB`;
    if (status === 0) return 'เชื่อมต่อเซิร์ฟเวอร์ไม่ได้ ตรวจการเชื่อมต่อแล้วลองใหม่';
    return `เกิดข้อผิดพลาดจากเซิร์ฟเวอร์ (HTTP ${status}) ลองใหม่อีกครั้ง`;
  }

  // Upload progress from XMLHttpRequest's upload events -> {percent, text} for the progress bar
  // (Issue #85). `total` is 0 when the browser cannot tell the size; then there is no percent.
  function uploadProgress(loaded, total) {
    const mb = (bytes) => `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    if (!total) return { percent: null, text: 'กำลังส่งไฟล์…' };
    const percent = Math.max(0, Math.min(100, Math.floor((loaded / total) * 100)));
    if (percent >= 100) return { percent: 100, text: 'ส่งไฟล์ครบแล้ว รอเซิร์ฟเวอร์บันทึกโน้ต…' };
    return { percent, text: `กำลังส่งไฟล์ ${percent}% (${mb(loaded)} จาก ${mb(total)})` };
  }

  // The search page with the new note's title as the search text.
  function searchUrlFor(note) {
    return `/?${new URLSearchParams({ q: note.title })}`;
  }

  const UploadUtils = {
    REQUIRED_FIELDS,
    OPTIONAL_FIELDS,
    MAX_FILE_BYTES,
    validateMetadata,
    validateUpload,
    uploadFields,
    uploadErrorMessage,
    uploadProgress,
    searchUrlFor,
  };

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = UploadUtils;
  } else {
    exportTo.UploadUtils = UploadUtils;
  }
})(typeof window !== 'undefined' ? window : globalThis);
