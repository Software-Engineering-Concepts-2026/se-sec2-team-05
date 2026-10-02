# Web gateway container image (ADR-006) — nginx ที่เสิร์ฟหน้าเว็บและ proxy ไป notes/auth service
# ใช้ nginx-unprivileged ให้รันเป็น non-root เหมือน image ของ service อื่น · pin เวอร์ชัน base image
# build context คือโฟลเดอร์นี้: docker build -t noteshare/web web
FROM nginxinc/nginx-unprivileged:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
# copy ทีละไฟล์ ไม่ให้ไฟล์เทสต์หรือ README หลุดไปถูกเสิร์ฟ
COPY index.html login.html upload.html style.css \
     app.js site.js login.js upload.js search-utils.js session-utils.js upload-utils.js \
     /usr/share/nginx/html/
EXPOSE 8080
