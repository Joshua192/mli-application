FROM python:3.11.11

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*


# Install regular dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

EXPOSE 8501

CMD ["streamlit", "run", "stream.py", "--server.port=8501", "--server.address=0.0.0.0"]


# MY MESSY DOCKER COMPOSE

# FROM python:3.11.11

# WORKDIR /MLI-APPLICATION

# COPY requirements.txt .

# RUN pip install -r ./requirements.txt

# COPY src/ .

# RUN streamlit run stream.py

# COPY . .

# ENV PORT=8501

# EXPOSE 8501

# CMD [ "streamlit","run", "stream.py" ]