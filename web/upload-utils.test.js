const test = require('node:test');
const assert = require('node:assert/strict');
const {
  REQUIRED_FIELDS,
  MAX_FILE_BYTES,
  validateMetadata,
  validateUpload,
  uploadFields,
  uploadErrorMessage,
  uploadProgress,
  uploadTicketRequest,
  blobUploadHeaders,
  directNoteBody,
  blobUploadErrorMessage,
  searchUrlFor,
} = require('./upload-utils.js');

const goodFields = {
  title: 'สรุป Calculus บทที่ 3',
  subject_name: 'Calculus I',
  subject_code: '01418112',
  faculty: 'ICT',
  year_level: '1',
  lesson: 'อนุพันธ์',
  topic: '',
  class_date: '',
  description: '',
};
const pdf = { name: 'calc.pdf', size: 1024, type: 'application/pdf' };

test('validateUpload passes a complete form with a PDF', () => {
  assert.deepEqual(validateUpload(goodFields, pdf), {});
});

test('validateUpload reports every missing required field and the file at once', () => {
  const errors = validateUpload({ title: '   ' }, null);
  assert.deepEqual(Object.keys(errors).sort(), [...REQUIRED_FIELDS, 'file'].sort());
  assert.equal(errors.title, 'จำเป็นต้องกรอก');
  assert.equal(errors.file, 'ต้องแนบไฟล์โน้ต');
});

test('validateUpload uses the same length limits as validation.py', () => {
  const errors = validateUpload(
    { ...goodFields, title: 'a'.repeat(201), subject_code: 'C'.repeat(31), topic: 't'.repeat(201) },
    pdf,
  );
  assert.equal(errors.title, 'ยาวเกิน 200 ตัวอักษร');
  assert.equal(errors.subject_code, 'ยาวเกิน 30 ตัวอักษร');
  assert.equal(errors.topic, 'ยาวเกิน 200 ตัวอักษร');
  assert.deepEqual(validateUpload({ ...goodFields, title: 'a'.repeat(200) }, pdf), {});
});

test('validateUpload accepts year 1 to 8 only', () => {
  assert.equal(validateUpload({ ...goodFields, year_level: '0' }, pdf).year_level, 'ต้องอยู่ระหว่าง 1-8');
  assert.equal(validateUpload({ ...goodFields, year_level: '9' }, pdf).year_level, 'ต้องอยู่ระหว่าง 1-8');
  assert.equal(validateUpload({ ...goodFields, year_level: 'two' }, pdf).year_level, 'ต้องเป็นตัวเลข');
  assert.deepEqual(validateUpload({ ...goodFields, year_level: '8' }, pdf), {});
});

test('validateUpload checks class_date is a real YYYY-MM-DD date when given', () => {
  assert.deepEqual(validateUpload({ ...goodFields, class_date: '2026-08-20' }, pdf), {});
  for (const bad of ['20/08/2026', '2026-02-30', '2026-13-01']) {
    assert.equal(validateUpload({ ...goodFields, class_date: bad }, pdf).class_date, 'ต้องเป็นรูปแบบ YYYY-MM-DD', bad);
  }
});

test('validateUpload takes PDF, PNG and JPG only', () => {
  assert.deepEqual(validateUpload(goodFields, { name: 'a.png', size: 10, type: 'image/png' }), {});
  assert.deepEqual(validateUpload(goodFields, { name: 'a.jpeg', size: 10, type: 'image/jpeg' }), {});
  for (const type of ['application/msword', 'image/gif', '']) {
    assert.equal(validateUpload(goodFields, { name: 'a.x', size: 10, type }).file, 'รองรับเฉพาะไฟล์ PDF, PNG และ JPG', type);
  }
});

test('validateUpload rejects an empty file and one over 10 MB (NFR-006, ADR-012)', () => {
  assert.equal(MAX_FILE_BYTES, 10 * 1024 * 1024);
  assert.equal(validateUpload(goodFields, { ...pdf, size: 0 }).file, 'ไฟล์ว่าง');
  assert.equal(validateUpload(goodFields, { ...pdf, size: MAX_FILE_BYTES + 1 }).file, 'ไฟล์ใหญ่เกิน 10 MB');
  assert.deepEqual(validateUpload(goodFields, { ...pdf, size: MAX_FILE_BYTES }), {});
});

test('uploadFields trims values and leaves out empty optional fields', () => {
  assert.deepEqual(uploadFields({ ...goodFields, title: '  Calc  ', topic: ' Chain rule ', uploader_name: 'Someone else' }), {
    title: 'Calc',
    subject_name: 'Calculus I',
    subject_code: '01418112',
    faculty: 'ICT',
    year_level: '1',
    lesson: 'อนุพันธ์',
    topic: 'Chain rule',
  });
});

test('uploadErrorMessage covers notes-service errors and the gateway size limit', () => {
  assert.match(uploadErrorMessage(400, { error: 'validation_failed', fields: { file: 'x' } }), /ช่องที่มีข้อความสีแดง/);
  assert.match(uploadErrorMessage(401, { error: 'unauthorized' }), /เข้าสู่ระบบใหม่/);
  assert.match(uploadErrorMessage(503, { error: 'auth_unavailable' }), /ไม่พร้อมใช้งาน/);
  assert.equal(uploadErrorMessage(413, null), 'ไฟล์ใหญ่เกิน 10 MB');
  assert.match(uploadErrorMessage(409, { error: 'upload_already_used' }), /ถูกใช้สร้างโน้ตไปแล้ว/);
  assert.match(uploadErrorMessage(0, null), /เชื่อมต่อเซิร์ฟเวอร์ไม่ได้/);
  assert.match(uploadErrorMessage(500, null), /HTTP 500/);
});

test('searchUrlFor opens the search page on the new note', () => {
  assert.equal(searchUrlFor({ title: 'Linked List & Stack' }), '/?q=Linked+List+%26+Stack');
});

test('validateMetadata checks the text fields only, for the profile edit form', () => {
  assert.deepEqual(validateMetadata(goodFields), {});
  const errors = validateMetadata({ ...goodFields, title: ' ', year_level: '9', class_date: '2026-02-30' });
  assert.deepEqual(Object.keys(errors).sort(), ['class_date', 'title', 'year_level']);
  assert.equal(errors.file, undefined);
});

test('uploadProgress turns upload events into a percent and a Thai line (Issue #85)', () => {
  const mb = 1024 * 1024;
  assert.deepEqual(uploadProgress(0, 10 * mb), { percent: 0, text: 'กำลังส่งไฟล์ 0% (0.0 MB จาก 10.0 MB)' });
  assert.deepEqual(uploadProgress(4.5 * mb, 10 * mb), { percent: 45, text: 'กำลังส่งไฟล์ 45% (4.5 MB จาก 10.0 MB)' });
  // 99.9% is not done yet: the bar must not claim 100 before the last byte
  assert.equal(uploadProgress(10 * mb - 1, 10 * mb).percent, 99);
  assert.deepEqual(uploadProgress(10 * mb, 10 * mb), { percent: 100, text: 'ส่งไฟล์ครบแล้ว รอเซิร์ฟเวอร์บันทึกโน้ต…' });
  // size unknown (lengthComputable = false): no percent
  assert.deepEqual(uploadProgress(500, 0), { percent: null, text: 'กำลังส่งไฟล์…' });
});

// ADR-012: direct upload to Vercel Blob
const ticket = {
  mode: 'direct',
  pathname: 'uploads/7/0123456789abcdef0123456789abcdef.pdf',
  upload_url: 'https://vercel.com/api/blob/?pathname=uploads%2F7%2F0123456789abcdef0123456789abcdef.pdf',
  client_token: 'vercel_blob_client_store1_abc',
  store_id: 'store1',
  api_version: '12',
};
const bigPdf = { name: 'Week 3.PDF', size: 9 * 1024 * 1024, type: 'Application/PDF' };

test('uploadTicketRequest sends the name, type and size the service checks', () => {
  assert.deepEqual(uploadTicketRequest(bigPdf), {
    file_name: 'Week 3.PDF',
    content_type: 'application/pdf',
    size_bytes: 9 * 1024 * 1024,
  });
});

test('blobUploadHeaders match what @vercel/blob/client put sends with a client token', () => {
  assert.deepEqual(blobUploadHeaders(ticket, bigPdf), {
    authorization: 'Bearer vercel_blob_client_store1_abc',
    'x-api-version': '12',
    'x-vercel-blob-access': 'private',
    'x-vercel-blob-store-id': 'store1',
    'x-content-type': 'application/pdf',
    'x-content-length': String(9 * 1024 * 1024),
  });
});

test('directNoteBody is the form fields plus where the file went, nothing from the ticket token', () => {
  const body = directNoteBody({ ...goodFields, topic: ' ' }, ticket, bigPdf);
  assert.deepEqual(body, {
    ...uploadFields(goodFields),
    file_name: 'Week 3.PDF',
    upload_pathname: 'uploads/7/0123456789abcdef0123456789abcdef.pdf',
  });
  assert.equal(JSON.stringify(body).includes('vercel_blob_client'), false);
});

test('blobUploadErrorMessage explains a failed PUT to Blob', () => {
  assert.match(blobUploadErrorMessage(0), /ตรวจการเชื่อมต่อ/);
  assert.match(blobUploadErrorMessage(403), /หมดอายุ/);
  assert.match(blobUploadErrorMessage(500), /HTTP 500/);
});
