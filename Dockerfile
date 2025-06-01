FROM python:3.11
WORKDIR /app
COPY requirements.txt /app
RUN pip3 install -r requirements.txt --no-cache-dir
COPY gradio_biographer.py /app
COPY config_en.json /app
COPY config_ru.json /app

# # Expose Gradio port
# EXPOSE 7860

# # Set environment variables
# ENV PYTHONUNBUFFERED=1
# ENV GRADIO_SERVER_NAME=0.0.0.0
# ENV GRADIO_SERVER_PORT=7860

# Command to run the application
CMD ["python", "gradio_biographer.py"] 