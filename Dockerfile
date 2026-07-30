FROM python:3.10-slim

WORKDIR /app

# Install required packages for your bot
RUN pip install pyTelegramBotAPI requests urllib3

# Copy only the bot code
COPY bot.py .

# Expose port for Dummy Server (Render bypass)
EXPOSE 7860

# Run the bot
CMD ["python", "bot.py"]
