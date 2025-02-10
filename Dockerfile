# Utilize a imagem oficial do Python como base
FROM python:3.10-slim

# Defina o diretório de trabalho
WORKDIR /app

# Copie o requirements.txt para o diretório de trabalho
COPY requirements.txt .

# Instale as dependências
RUN pip install -r requirements.txt

# Instale as dependências do SO
RUN apt-get update && apt-get install -y \
    libgl1 \
    cmake \
    libssl-dev \
    libglib2.0-0

# Copie o código do projeto para o diretório de trabalho
COPY . .

# Exponha a porta 8501 para o Streamlit
EXPOSE 8501

# Defina a variável de ambiente para o Streamlit
ENV STREAMLIT_SERVER_PORT=8501

# Defina a variável de ambiente para o Google Cloud Vision API
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/util/palavra-mestra.json

# Defina o comando para executar o Streamlit
CMD ["streamlit", "run", "app.py"]