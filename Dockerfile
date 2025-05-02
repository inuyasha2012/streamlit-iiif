FROM docker.1ms.run/python:3.12.3
LABEL authors="inuyasha"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Use the PORT environment variable
EXPOSE 8501

# Use the PORT environment variable in the command
CMD ["sh", "-c", "streamlit run app.py --server.address=0.0.0.0 --server.port=8501"]