FROM python:3.9-slim

# Instalar mysql-client para o mysqladmin
RUN apt-get update && apt-get install -y \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Tornar o script de inicialização executável
RUN chmod +x start.sh

# Definir variáveis de ambiente padrão
ENV MYSQL_HOST=db
ENV MYSQL_USER=user
ENV MYSQL_PASSWORD=password

CMD ["./start.sh"]