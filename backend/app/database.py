import os
import time
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database URL - ajustada para funcionar no Docker
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://user:password@db:3306/app_db")

# Configuração do engine com retry e configurações de pool
def create_db_engine():
    max_retries = 10
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            engine = create_engine(
                DATABASE_URL, 
                echo=True,
                pool_pre_ping=True,  # Verifica conexões antes de usar
                pool_recycle=3600,   # Recicla conexões após 1 hora
                pool_size=10,        # Número de conexões no pool
                max_overflow=20      # Máximo de conexões extras
            )
            
            # Testa a conexão
            with engine.connect() as conn:
                from sqlalchemy import text
                conn.execute(text("SELECT 1"))
                
            logger.info("✅ Conexão com banco de dados estabelecida com sucesso")
            return engine
            
        except Exception as e:
            logger.warning(f"⚠️  Tentativa {attempt + 1}/{max_retries} de conexão falhou: {e}")
            if attempt < max_retries - 1:
                logger.info(f"🔄 Tentando novamente em {retry_delay} segundos...")
                time.sleep(retry_delay)
            else:
                logger.error("❌ Falha ao conectar ao banco após todas as tentativas")
                raise

# Criar engine e session
try:
    engine = create_db_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("🔗 Engine e SessionLocal configurados")
except Exception as e:
    logger.error(f"❌ Erro crítico ao configurar banco de dados: {e}")
    raise

Base = declarative_base()

def get_db():
    """Dependency que fornece uma sessão do banco de dados"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Erro na sessão do banco: {e}")
        db.rollback()
        raise
    finally:
        db.close() 