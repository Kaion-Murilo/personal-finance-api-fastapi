FROM python:3.11-slim

# diretório de trabalho dentro do container
WORKDIR /app

# copia e instala dependências primeiro (cache do Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copia o resto do projeto
COPY . .

# porta que o uvicorn vai rodar
EXPOSE 8000

# comando para iniciar a API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]