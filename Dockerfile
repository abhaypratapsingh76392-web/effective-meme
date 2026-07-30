FROM python:3.10-slim

WORKDIR /app

# Install required packages
RUN pip install pyTelegramBotAPI requests urllib3

# Copy the bot code
COPY bot.py .

# Expose port for Dummy Server (Render bypass)
EXPOSE 7860

# Run the bot
CMD ["python", "bot.py"]
