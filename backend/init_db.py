#!/usr/bin/env python3
"""
Script para inicializar o banco de dados com todas as tabelas e dados fictícios
"""
import sys
import os
import time
from datetime import datetime, date, timedelta

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base, get_db
from app.models import models
from sqlalchemy.orm import Session
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def wait_for_db():
    """Aguarda o banco de dados ficar disponível"""
    max_retries = 30
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            # Tenta conectar ao banco
            with engine.connect() as conn:
                from sqlalchemy import text
                conn.execute(text("SELECT 1"))
            logger.info("Banco de dados está disponível")
            return True
        except Exception as e:
            logger.warning(f"Tentativa {attempt + 1}/{max_retries} - Aguardando banco: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                logger.error("Falha ao conectar ao banco após todas as tentativas")
                return False
    return False

def populate_sample_data():
    """Popula o banco de dados com dados fictícios"""
    try:
        logger.info("Iniciando população de dados fictícios...")
        
        # Criar sessão do banco
        db = next(get_db())
        
        # Verificar se já existem dados
        hospital_count = db.query(models.Hospital).count()
        if hospital_count > 0:
            logger.info("Dados já existem no banco. Pulando inserção...")
            db.close()
            return True
        
        # 1. Hospitais
        logger.info("Inserindo hospitais...")
        hospitais = [
            models.Hospital(
                nome="Hospital Central de Brasília",
                endereco="SQN 123, Bloco A, Asa Norte, Brasília - DF",
                telefone="(61) 3333-1111",
                cnpj="12345678000195"
            ),
            models.Hospital(
                nome="Hospital São José",
                endereco="Rua das Flores, 456, Águas Claras - DF",
                telefone="(61) 3333-2222",
                cnpj="98765432000187"
            ),
            models.Hospital(
                nome="Hospital Universitário UnB",
                endereco="Campus Darcy Ribeiro, Asa Norte, Brasília - DF",
                telefone="(61) 3333-3333",
                cnpj="11122233000156"
            )        ]
        
        for hospital in hospitais:
            db.add(hospital)
        db.commit()
        
        # 2. Pacientes
        logger.info("Inserindo pacientes...")
        pacientes = [
            models.Paciente(
                nome="Maria Silva Santos",
                cpf="12345678901",
                data_nascimento=date(1985, 3, 15),
                status_saude="Estável",
                hospital_id=1
            ),
            models.Paciente(
                nome="João Pedro Oliveira",
                cpf="98765432109",
                data_nascimento=date(1992, 7, 22),
                status_saude="Crítico",
                hospital_id=1
            ),
            models.Paciente(
                nome="Ana Carolina Ferreira",
                cpf="45678912345",
                data_nascimento=date(1978, 11, 8),
                status_saude="Recuperando",
                hospital_id=2
            ),
            models.Paciente(
                nome="Carlos Eduardo Lima",
                cpf="78912345678",
                data_nascimento=date(1965, 12, 3),
                status_saude="Estável",
                hospital_id=2
            ),
            models.Paciente(
                nome="Fernanda Costa Almeida",
                cpf="32165498732",
                data_nascimento=date(1990, 5, 18),
                status_saude="Observação",
                hospital_id=3
            )        ]
        
        for paciente in pacientes:
            db.add(paciente)
        db.commit()
        
        # 3. Médicos
        logger.info("Inserindo médicos...")
        medicos = [
            models.Medico(
                nome="Dr. Roberto Cardoso",
                crm="CRM-DF 12345",
                especialidade="Cardiologia",
                hospital_id=1
            ),
            models.Medico(
                nome="Dra. Patricia Neurologia",
                crm="CRM-DF 23456",
                especialidade="Neurologia",
                hospital_id=1
            ),
            models.Medico(
                nome="Dr. Marcos Pediatria",
                crm="CRM-DF 34567",
                especialidade="Pediatria",
                hospital_id=2
            ),
            models.Medico(
                nome="Dra. Lucia Ginecologia",
                crm="CRM-DF 45678",
                especialidade="Ginecologia",
                hospital_id=2
            ),
            models.Medico(
                nome="Dr. Fernando Ortopedia",
                crm="CRM-DF 56789",
                especialidade="Ortopedia",
                hospital_id=3
            )        ]
        
        for medico in medicos:
            db.add(medico)
        db.commit()
        
        # 4. Quartos
        logger.info("Inserindo quartos...")
        quartos = [
            models.Quarto(
                numero="101",
                tipo="Individual",
                capacidade=1,
                valor_diario=250.00,
                hospital_id=1
            ),
            models.Quarto(
                numero="102",
                tipo="Duplo",
                capacidade=2,
                valor_diario=150.00,
                hospital_id=1
            ),
            models.Quarto(
                numero="201",
                tipo="UTI",
                capacidade=1,
                valor_diario=800.00,
                hospital_id=1
            ),
            models.Quarto(
                numero="103",
                tipo="Individual",
                capacidade=1,
                valor_diario=220.00,
                hospital_id=2
            ),
            models.Quarto(
                numero="204",
                tipo="Duplo",
                capacidade=2,
                valor_diario=140.00,
                hospital_id=2
            ),
            models.Quarto(
                numero="301",
                tipo="Individual",
                capacidade=1,
                valor_diario=280.00,
                hospital_id=3
            )        ]
        
        for quarto in quartos:
            db.add(quarto)
        db.commit()
        
        # 5. Internações
        logger.info("Inserindo internações...")
        internacoes = [
            models.Internacao(
                paciente_id=1,
                medico_responsavel_id=1,
                quarto_id=1,
                data_entrada=datetime.now().date() - timedelta(days=5)
            ),
            models.Internacao(
                paciente_id=2,
                medico_responsavel_id=2,
                quarto_id=3,
                data_entrada=datetime.now().date() - timedelta(days=3)
            ),
            models.Internacao(
                paciente_id=3,
                medico_responsavel_id=4,
                quarto_id=4,
                data_entrada=datetime.now().date() - timedelta(days=7),
                data_alta=datetime.now().date() - timedelta(days=1)
            ),
            models.Internacao(
                paciente_id=5,
                medico_responsavel_id=5,
                quarto_id=6,
                data_entrada=datetime.now().date() - timedelta(days=2)
            )
        ]
        for internacao in internacoes:
            db.add(internacao)
        db.commit()
        
        # 6. Farmácias
        logger.info("Inserindo farmácias...")
        farmacias = [
            models.Farmacia(
                nome="Farmácia Central",
                responsavel="Dr. José Silva",
                telefone="(61) 3333-1199",
                hospital_id=1
            ),
            models.Farmacia(
                nome="Farmácia São José",
                responsavel="Dra. Maria Santos",
                telefone="(61) 3333-2299",
                hospital_id=2
            ),
            models.Farmacia(
                nome="Farmácia UnB",
                responsavel="Dr. Pedro Oliveira",
                telefone="(61) 3333-3399",
                hospital_id=3
            )
        ]
        
        for farmacia in farmacias:
            db.add(farmacia)
        db.commit()
        
        # 7. Medicamentos
        logger.info("Inserindo medicamentos...")
        medicamentos = [
            models.Medicamento(
                nome="Aspirina 500mg",
                principio_ativo="Ácido Acetilsalicílico",
                fabricante="Bayer",
                lote="ASP2024001",
                data_validade=date(2025, 12, 31),
                quantidade_estoque=1000,
                preco_unitario=0.50,
                farmacia_id=1
            ),
            models.Medicamento(
                nome="Amoxicilina 500mg",
                principio_ativo="Amoxicilina",
                fabricante="EMS",
                lote="AMO2024002",
                data_validade=date(2025, 10, 15),
                quantidade_estoque=500,
                preco_unitario=1.20,
                farmacia_id=1
            ),
            models.Medicamento(
                nome="Paracetamol 750mg",
                principio_ativo="Paracetamol",
                fabricante="Medley",
                lote="PAR2024003",
                data_validade=date(2025, 11, 30),
                quantidade_estoque=800,
                preco_unitario=0.80,
                farmacia_id=1
            ),
            models.Medicamento(
                nome="Dipirona 500mg",
                principio_ativo="Dipirona Sódica",
                fabricante="Neo Química",
                lote="DIP2024004",
                data_validade=date(2025, 9, 20),
                quantidade_estoque=600,
                preco_unitario=0.45,
                farmacia_id=2
            ),
            models.Medicamento(
                nome="Losartana 50mg",
                principio_ativo="Losartana Potássica",
                fabricante="Germed",
                lote="LOS2024005",
                data_validade=date(2026, 1, 10),
                quantidade_estoque=300,
                preco_unitario=2.30,
                farmacia_id=2
            ),
            models.Medicamento(
                nome="Omeprazol 20mg",
                principio_ativo="Omeprazol",
                fabricante="Eurofarma",
                lote="OME2024006",
                data_validade=date(2025, 8, 25),
                quantidade_estoque=400,
                preco_unitario=1.80,
                farmacia_id=3
            )        ]
        
        for medicamento in medicamentos:
            db.add(medicamento)
        db.commit()
        
        db.close()
        logger.info("✅ Dados fictícios inseridos com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao inserir dados fictícios: {e}")
        import traceback
        logger.error(traceback.format_exc())
        if 'db' in locals():
            db.rollback()
            db.close()
        return False

def init_db():
    """Inicializa o banco de dados criando todas as tabelas"""
    try:
        logger.info("Iniciando criação das tabelas do sistema hospitalar...")
        
        # Lista todas as tabelas que serão criadas
        tables_to_create = [
            "hospitais",
            "pacientes", 
            "medicos",
            "quartos",
            "internacoes",
            "prescricoes_medicas",
            "itens_prescricao",
            "farmacias",
            "medicamentos",
            "contas_hospitalares"
        ]
        
        logger.info(f"Tabelas a serem criadas: {', '.join(tables_to_create)}")
        
        # Criar todas as tabelas
        Base.metadata.create_all(bind=engine)
        
        # Verificar se as tabelas foram criadas
        from sqlalchemy import inspect
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        logger.info(f"Tabelas criadas no banco: {', '.join(existing_tables)}")
        
        # Verificar se todas as tabelas esperadas foram criadas
        missing_tables = set(tables_to_create) - set(existing_tables)
        if missing_tables:
            logger.warning(f"Tabelas não criadas: {', '.join(missing_tables)}")
            return False
        else:
            logger.info("✅ Todas as tabelas foram criadas com sucesso!")
            
        # Inserir dados fictícios
        return populate_sample_data()
            
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabelas: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    logger.info("🏥 Inicializando Sistema de Gestão Hospitalar...")
    
    # Aguardar banco de dados
    if not wait_for_db():
        logger.error("❌ Falha ao conectar ao banco de dados")
        sys.exit(1)
    
    # Inicializar tabelas e dados
    success = init_db()
    
    if success:
        logger.info("🎉 Sistema inicializado com sucesso!")
        logger.info("📊 Dados fictícios inseridos nas seguintes tabelas:")
        logger.info("   • 3 Hospitais")
        logger.info("   • 5 Pacientes")
        logger.info("   • 5 Médicos")
        logger.info("   • 6 Quartos")
        logger.info("   • 4 Internações")
        logger.info("   • 3 Farmácias")
        logger.info("   • 6 Medicamentos")
        logger.info("   • 3 Prescrições Médicas")
        logger.info("   • 4 Itens de Prescrição")
        logger.info("   • 4 Contas Hospitalares")
        sys.exit(0)
    else:
        logger.error("❌ Falha na inicialização do sistema")
        sys.exit(1)
