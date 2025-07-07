# Sistema de Gestão Hospitalar

## Arquitetura do Projeto

Este é um monorepo contendo:
- **Backend**: API FastAPI com SQLAlchemy
- **Frontend**: Interface web moderna
- **Docs**: Documentação completa
- **Scripts**: Automação e deploy

## Estrutura
```
├── backend/           # API FastAPI
├── frontend/          # Interface web
├── docs/             # Documentação
├── scripts/          # Scripts de automação
└── docker-compose.yml # Orquestração
```

## Quick Start
```bash
# Iniciar todos os serviços
docker-compose up

# Desenvolvimento
./scripts/start-dev.sh

# Testes
./scripts/run-tests.sh
```

## Tecnologias
- **Backend**: FastAPI, SQLAlchemy, MySQL
- **Frontend**: React/Vue, TypeScript
- **Infraestrutura**: Docker, Nginx
- **Testes**: Pytest, Jest/Vitest
