const test = require('node:test');
const assert = require('node:assert/strict');
const {
  TOKEN_HEADER,
  MAX_TOKEN_LENGTH,
  tokenProblem,
  tokenHeaders,
  tokenCheckResult,
  editErrorMessage,
} = require('./edit-utils.js');

test('tokenProblem accepts a copied token, spaces around it included', () => {
  assert.equal(tokenProblem('pD3x_k9-QmZ1aB7c'), '');
  assert.equal(tokenProblem('  pD3x_k9-QmZ1aB7c \n'), '');
});

test('tokenProblem rejects an empty, broken or oversized token', () => {
  assert.match(tokenProblem(''), /กรอกรหัสแก้ไข/);
  assert.match(tokenProblem('   '), /กรอกรหัสแก้ไข/);
  assert.match(tokenProblem(undefined), /กรอกรหัสแก้ไข/);
  assert.match(tokenProblem('pD3x k9'), /ช่องว่าง/);
  assert.match(tokenProblem('a'.repeat(MAX_TOKEN_LENGTH + 1)), /ยาวเกิน 200/);
  assert.equal(tokenProblem('a'.repeat(MAX_TOKEN_LENGTH)), '');
});

test('tokenHeaders sends only the trimmed token header, never Authorization', () => {
  assert.equal(TOKEN_HEADER, 'X-Note-Token');
  assert.deepEqual(tokenHeaders('  abc_123 '), { 'X-Note-Token': 'abc_123' });
  assert.ok(!('Authorization' in tokenHeaders('abc')));
});

test('tokenCheckResult reads the answer of an empty PATCH', () => {
  assert.equal(tokenCheckResult(400, { error: 'no_fields_to_update' }), 'valid');
  assert.equal(tokenCheckResult(403, { error: 'forbidden' }), 'wrong');
  assert.equal(tokenCheckResult(404, { error: 'not_found' }), 'gone');
  // a 400 for another reason, or a 200 (something was written), is not a token answer
  assert.equal(tokenCheckResult(400, { error: 'validation_failed', fields: {} }), 'error');
  assert.equal(tokenCheckResult(200, { id: 7 }), 'error');
  assert.equal(tokenCheckResult(401, { error: 'unauthorized' }), 'error');
  assert.equal(tokenCheckResult(0, null), 'error');
});

test('editErrorMessage covers PATCH/DELETE with a token', () => {
  assert.match(editErrorMessage(403, { error: 'forbidden' }), /รหัสแก้ไขไม่ถูกต้อง/);
  assert.match(editErrorMessage(400, { error: 'validation_failed', fields: {} }), /สีแดง/);
  assert.match(editErrorMessage(400, { error: 'no_fields_to_update' }), /ยังไม่ได้แก้/);
  assert.match(editErrorMessage(404, { error: 'not_found' }), /ไม่พบโน้ตนี้แล้ว/);
  assert.match(editErrorMessage(413, null), /HTTP 413/);
  assert.match(editErrorMessage(0, null), /เชื่อมต่อเซิร์ฟเวอร์ไม่ได้/);
});
