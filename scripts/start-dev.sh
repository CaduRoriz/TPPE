#!/bin/bash
# Script para iniciar o ambiente de desenvolvimento

echo "🚀 Iniciando ambiente de desenvolvimento..."

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando. Por favor, inicie o Docker."
    exit 1
fi

# Construir e iniciar serviços
echo "📦 Construindo containers..."
docker-compose build

echo "🔄 Iniciando serviços..."
docker-compose up -d

echo "⏳ Aguardando serviços ficarem prontos..."
sleep 10

echo "✅ Ambiente iniciado com sucesso!"
echo ""
echo "🌐 Backend: http://localhost:8000"
echo "🌐 Frontend: http://localhost:3000"
echo "📚 Docs API: http://localhost:8000/docs"
echo ""
echo "Para parar: docker-compose down"
