# Stats Service container image — see docs/architecture/c4-container.md
FROM python:3.12-slim AS deps
WORKDIR /app
COPY services/stats-service/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
RUN useradd --create-home --shell /usr/sbin/nologin appuser
COPY --from=deps --chown=appuser:appuser /root/.local /home/appuser/.local
COPY --chown=appuser:appuser services/stats-service/app.py .
ENV PATH=/home/appuser/.local/bin:$PATH
EXPOSE 5000
USER appuser
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
