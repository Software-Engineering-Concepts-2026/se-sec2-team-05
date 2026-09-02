# Notes Service container image — โครงเดียวกับ root Dockerfile ของ Stats Service
# (multi-stage, base image pin เวอร์ชัน, รันด้วย non-root user)
# build context คือโฟลเดอร์นี้: docker build -t noteshare/notes-service services/notes-service
FROM python:3.12-slim AS deps
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
RUN useradd --create-home --shell /usr/sbin/nologin appuser
COPY --from=deps --chown=appuser:appuser /root/.local /home/appuser/.local
COPY --chown=appuser:appuser app.py models.py storage.py validation.py ./
# โฟลเดอร์เก็บไฟล์โน้ต — compose mount volume ทับตรงนี้ให้ข้อมูลอยู่รอด container restart
RUN mkdir -p /data/notes && chown appuser:appuser /data/notes
ENV PATH=/home/appuser/.local/bin:$PATH \
    NOTES_STORAGE_DIR=/data/notes
EXPOSE 5001
USER appuser
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "app:app"]
