FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Environment variables (must be provided at runtime)
ENV TELEGRAM_BOT_TOKEN=""
ENV ANTHROPIC_API_KEY=""

# Run bot
CMD ["python", "-m", "src.bot.telegram_bot"]
