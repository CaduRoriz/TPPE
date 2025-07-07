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
python /app/init_db.py || echo "⚠️ Houve problemas na inicialização do banco, mas continuando..."

# Não executa testes automaticamente - eles rodam em container separado
# echo "Executando testes..."
# python -m pytest /app/tests/ -v --tb=short || echo "⚠️ Alguns testes falharam, mas a aplicação continuará"

# Inicia a aplicação
echo "Iniciando aplicação FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
