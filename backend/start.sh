#!/bin/bash
# Script de inicialização do container
echo "Aguardando banco de dados ficar disponível..."

# Aguarda o banco de dados ficar disponível
while ! mysqladmin ping -h"$MYSQL_HOST" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" --silent; do
    echo "Aguardando MySQL..."
    sleep 2
done

echo "Banco de dados disponível!"

# Executa o script de inicialização do banco
echo "Inicializando tabelas do banco de dados..."
python /app/init_db.py

# Inicia a aplicação
echo "Iniciando aplicação FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
