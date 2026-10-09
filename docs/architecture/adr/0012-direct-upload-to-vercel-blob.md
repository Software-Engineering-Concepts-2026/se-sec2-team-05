# ADR-012: Upload Note Files Directly to Vercel Blob

🌐 **English** · [ภาษาไทย](./0012-direct-upload-to-vercel-blob.th.md)

**Status:** Accepted

**Context:**
NFR-003 and NFR-006 allow note files up to 10 MB. ADR-009 lowered the limit to 4 MB everywhere because a Vercel Function accepts at most 4.5 MB of request body, and the upload form sent the file through notes-service. ADR-009 put off direct browser-to-Blob uploads because they need a token endpoint and changes to the upload page and the API. The Vercel Python SDK (`vercel` 0.11.4) can read and write Blob but cannot make client upload tokens; only the JavaScript package `@vercel/blob` can.

**Decision:**
*   On Vercel (`NOTES_STORAGE_BACKEND=blob`), the browser sends the file **straight to Vercel Blob**:
    1.  `POST /notes/uploads` (login required) with the file's name, type and size. notes-service checks them and returns a **client token** for one pathname under `uploads/<user id>/`, that type only, at most 10 MB, no overwrite, valid for 10 minutes.
    2.  The upload page PUTs the file to `https://vercel.com/api/blob/` with that token, using `XMLHttpRequest` for the progress bar.
    3.  `POST /notes` as JSON with the form fields, `file_name` and `upload_pathname`. notes-service accepts only a pathname under the caller's own `uploads/<id>/`, reads the size and type from Blob itself (not from the client), deletes the file if it breaks the rules, and answers `409` if that file already belongs to a note.
*   notes-service **signs client tokens itself** (`storage.generate_client_token`), with the same format as `generateClientTokenFromReadWriteToken` in `@vercel/blob` 2.8.0: an HMAC-SHA256 of the base64 JSON payload keyed with `BLOB_READ_WRITE_TOKEN`. A check against the real JavaScript function gave the same token byte for byte. The read-write token never leaves the server.
*   The page sends the PUT without a JavaScript library: the headers are the ones `put` from `@vercel/blob/client` sends, so the web app stays plain static files with no CDN dependency.
*   On compose (`LocalFileStorage`), `POST /notes/uploads` answers `mode: "form"` and the page posts the multipart form as before. The limit there goes back to **10 MB** (nginx `client_max_body_size 11m`).
*   On Vercel the multipart form path stays for other API clients, capped at 4 MB so a request never hits the 4.5 MB platform limit.

**Consequences:**
*   Notes up to 10 MB work on both Vercel and compose, as NFR-003/006 require, with real upload progress.
*   The token format is copied from `@vercel/blob`. If Vercel changes it, uploads on Vercel break until `generate_client_token` follows; BU-01 and the cross-check with the real package show where to look.
*   If a browser gets a token and uploads but never calls `POST /notes` (tab closed), the file stays in Blob under `uploads/<id>/` with no note. These orphans are bounded by the token's lifetime and size limit, and can be removed by listing that prefix; nothing removes them automatically yet.
*   Direct uploads can only be tested end to end on a real Vercel deployment; the pytest suite uses a fake Blob client.
