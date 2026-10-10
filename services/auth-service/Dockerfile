# User & Auth Service container image — โครงเดียวกับ Dockerfile ของ notes-service
# (multi-stage, base image pin เวอร์ชัน, รันด้วย non-root user)
# build context คือโฟลเดอร์นี้: docker build -t noteshare/auth-service services/auth-service
FROM python:3.12-slim AS deps
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
RUN useradd --create-home --shell /usr/sbin/nologin appuser
COPY --from=deps --chown=appuser:appuser /root/.local /home/appuser/.local
COPY --chown=appuser:appuser app.py auth_migrate.py auth_models.py auth_rate_limit.py auth_tokens.py credentials.py ./
COPY --chown=appuser:appuser migrations ./migrations
ENV PATH=/home/appuser/.local/bin:$PATH
# AUTH_JWT_SECRET ตั้งใจไม่ใส่ไว้ใน image — ต้องส่งเข้ามาตอนรัน (compose หรือ secret ของ host)
EXPOSE 5002
USER appuser
CMD ["gunicorn", "--bind", "0.0.0.0:5002", "app:app"]
