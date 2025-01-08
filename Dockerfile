# Use uma imagem base oficial com Python
FROM python:3.8-slim

# Configuração do ambiente (adiciona uma variável de ambiente para o caminho do arquivo de dados)
ENV DATA_FILE_PATH=/app/data/annotated_variants.tsv

# Instala dependências do sistema (opcional, ajuste conforme necessário)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Configure o diretório de trabalho no contêiner
WORKDIR /app

# Copie os arquivos do projeto para o contêiner
COPY . /app

# Instale as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Exponha a porta que será usada pela API Flask
EXPOSE 5000

# Comando para iniciar o servidor Flask
CMD ["python", "api/app.py"]
