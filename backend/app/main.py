from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging
from .database import engine, Base, get_db
from .models import models
from .schemas import schemas

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Hospital Management System", version="1.0.0")

@app.on_event("startup")
async def startup():
    try:
        # Criar todas as tabelas no banco de dados
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {e}")
        logger.warning("⚠️ Application will continue without database connection")
        # Não para a aplicação, apenas registra o erro

@app.get("/")
async def root():
    return {"message": "Hospital Management System API", "status": "running"}

@app.get("/health")
async def health_check():
    """Endpoint para verificar a saúde da aplicação e conexão com o banco"""
    try:
        # Tenta obter uma sessão do banco
        db = next(get_db())
        try:
            # Testa a conexão com o banco
            from sqlalchemy import text
            db.execute(text("SELECT 1"))
            db_status = "connected"
            status = "healthy"
        except Exception as db_error:
            logger.warning(f"Database connection issue: {db_error}")
            db_status = "disconnected"
            status = "degraded"
        finally:
            db.close()
            
        return {
            "status": status,
            "database": db_status,
            "message": "Sistema funcionando corretamente" if status == "healthy" else "Sistema com problemas de banco de dados"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail={
            "status": "unhealthy",
            "database": "error",
            "message": f"Erro no sistema: {str(e)}"
        })

# ========== HOSPITAL ENDPOINTS =========
@app.post("/hospitais/", response_model=schemas.Hospital)
def create_hospital(hospital: schemas.HospitalCreate, db: Session = Depends(get_db)):
    """Criar um novo hospital"""
    # Verificar se já existe hospital com o mesmo CNPJ
    db_hospital = db.query(models.Hospital).filter(models.Hospital.cnpj == hospital.cnpj).first()
    if db_hospital:
        raise HTTPException(status_code=400, detail="CNPJ já cadastrado")
    
    db_hospital = models.Hospital(**hospital.dict())
    db.add(db_hospital)
    db.commit()
    db.refresh(db_hospital)
    return db_hospital

@app.get("/hospitais/", response_model=List[schemas.Hospital])
def read_hospitals(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Listar todos os hospitais"""
    hospitals = db.query(models.Hospital).offset(skip).limit(limit).all()
    return hospitals

@app.get("/hospitais/{hospital_id}", response_model=schemas.Hospital)
def read_hospital(hospital_id: int, db: Session = Depends(get_db)):
    """Obter um hospital específico"""
    hospital = db.query(models.Hospital).filter(models.Hospital.id == hospital_id).first()
    if hospital is None:
        raise HTTPException(status_code=404, detail="Hospital não encontrado")
    return hospital

@app.put("/hospitais/{hospital_id}", response_model=schemas.Hospital)
def update_hospital(hospital_id: int, hospital: schemas.HospitalCreate, db: Session = Depends(get_db)):
    """Atualizar um hospital"""
    db_hospital = db.query(models.Hospital).filter(models.Hospital.id == hospital_id).first()
    if db_hospital is None:
        raise HTTPException(status_code=404, detail="Hospital não encontrado")
    
    for key, value in hospital.dict().items():
        setattr(db_hospital, key, value)
    
    db.commit()
    db.refresh(db_hospital)
    return db_hospital

@app.delete("/hospitais/{hospital_id}")
def delete_hospital(hospital_id: int, db: Session = Depends(get_db)):
    """Deletar um hospital"""
    db_hospital = db.query(models.Hospital).filter(models.Hospital.id == hospital_id).first()
    if db_hospital is None:
        raise HTTPException(status_code=404, detail="Hospital não encontrado")
    
    # Verificar se há pacientes vinculados ao hospital
    pacientes_count = db.query(models.Paciente).filter(models.Paciente.hospital_id == hospital_id).count()
    if pacientes_count > 0:
        raise HTTPException(status_code=400, detail=f"Não é possível deletar hospital com {pacientes_count} pacientes vinculados")
    
    # Verificar se há médicos vinculados ao hospital
    medicos_count = db.query(models.Medico).filter(models.Medico.hospital_id == hospital_id).count()
    if medicos_count > 0:
        raise HTTPException(status_code=400, detail=f"Não é possível deletar hospital com {medicos_count} médicos vinculados")
    
    # Verificar se há quartos vinculados ao hospital
    quartos_count = db.query(models.Quarto).filter(models.Quarto.hospital_id == hospital_id).count()
    if quartos_count > 0:
        raise HTTPException(status_code=400, detail=f"Não é possível deletar hospital com {quartos_count} quartos vinculados")
    
    db.delete(db_hospital)
    db.commit()
    return {"message": "Hospital deletado com sucesso"}

# ========== PACIENTE ENDPOINTS =========
@app.post("/pacientes/", response_model=schemas.Paciente)
def create_paciente(paciente: schemas.PacienteCreate, db: Session = Depends(get_db)):
    """Criar um novo paciente"""
    # Verificar se o hospital existe
    hospital = db.query(models.Hospital).filter(models.Hospital.id == paciente.hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital não encontrado")
    
    # Verificar se já existe paciente com o mesmo CPF
    db_paciente = db.query(models.Paciente).filter(models.Paciente.cpf == paciente.cpf).first()
    if db_paciente:
        raise HTTPException(status_code=400, detail="CPF já cadastrado")
    
    db_paciente = models.Paciente(**paciente.dict())
    db.add(db_paciente)
    db.commit()
    db.refresh(db_paciente)
    return db_paciente

@app.get("/pacientes/", response_model=List[schemas.Paciente])
def read_pacientes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Listar todos os pacientes"""
    pacientes = db.query(models.Paciente).offset(skip).limit(limit).all()
    return pacientes

@app.get("/pacientes/{paciente_id}", response_model=schemas.Paciente)
def read_paciente(paciente_id: int, db: Session = Depends(get_db)):
    """Obter um paciente específico"""
    paciente = db.query(models.Paciente).filter(models.Paciente.id == paciente_id).first()
    if paciente is None:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    return paciente

@app.put("/pacientes/{paciente_id}", response_model=schemas.Paciente)
def update_paciente(paciente_id: int, paciente: schemas.PacienteCreate, db: Session = Depends(get_db)):
    """Atualizar um paciente"""
    db_paciente = db.query(models.Paciente).filter(models.Paciente.id == paciente_id).first()
    if db_paciente is None:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    
    for key, value in paciente.dict().items():
        setattr(db_paciente, key, value)
    
    db.commit()
    db.refresh(db_paciente)
    return db_paciente

@app.delete("/pacientes/{paciente_id}")
def delete_paciente(paciente_id: int, db: Session = Depends(get_db)):
    """Deletar um paciente"""
    db_paciente = db.query(models.Paciente).filter(models.Paciente.id == paciente_id).first()
    if db_paciente is None:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    
    db.delete(db_paciente)
    db.commit()
    return {"message": "Paciente deletado com sucesso"}

# ========== MEDICO ENDPOINTS =========
@app.post("/medicos/", response_model=schemas.Medico)
def create_medico(medico: schemas.MedicoCreate, db: Session = Depends(get_db)):
    """Criar um novo médico"""
    # Verificar se o hospital existe
    hospital = db.query(models.Hospital).filter(models.Hospital.id == medico.hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital não encontrado")
    
    # Verificar se já existe médico com o mesmo CRM
    db_medico = db.query(models.Medico).filter(models.Medico.crm == medico.crm).first()
    if db_medico:
        raise HTTPException(status_code=400, detail="CRM já cadastrado")
    
    db_medico = models.Medico(**medico.dict())
    db.add(db_medico)
    db.commit()
    db.refresh(db_medico)
    return db_medico

@app.get("/medicos/", response_model=List[schemas.Medico])
def read_medicos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Listar todos os médicos"""
    medicos = db.query(models.Medico).offset(skip).limit(limit).all()
    return medicos

@app.get("/medicos/{medico_id}", response_model=schemas.Medico)
def read_medico(medico_id: int, db: Session = Depends(get_db)):
    """Obter um médico específico"""
    medico = db.query(models.Medico).filter(models.Medico.id == medico_id).first()
    if medico is None:
        raise HTTPException(status_code=404, detail="Médico não encontrado")
    return medico

@app.put("/medicos/{medico_id}", response_model=schemas.Medico)
def update_medico(medico_id: int, medico: schemas.MedicoCreate, db: Session = Depends(get_db)):
    """Atualizar um médico"""
    db_medico = db.query(models.Medico).filter(models.Medico.id == medico_id).first()
    if db_medico is None:
        raise HTTPException(status_code=404, detail="Médico não encontrado")
    
    for key, value in medico.dict().items():
        setattr(db_medico, key, value)
    
    db.commit()
    db.refresh(db_medico)
    return db_medico

@app.delete("/medicos/{medico_id}")
def delete_medico(medico_id: int, db: Session = Depends(get_db)):
    """Deletar um médico"""
    db_medico = db.query(models.Medico).filter(models.Medico.id == medico_id).first()
    if db_medico is None:
        raise HTTPException(status_code=404, detail="Médico não encontrado")
    
    db.delete(db_medico)
    db.commit()
    return {"message": "Médico deletado com sucesso"}

# ========== QUARTO ENDPOINTS =========
@app.post("/quartos/", response_model=schemas.Quarto)
def create_quarto(quarto: schemas.QuartoCreate, db: Session = Depends(get_db)):
    """Criar um novo quarto"""
    # Verificar se o hospital existe
    hospital = db.query(models.Hospital).filter(models.Hospital.id == quarto.hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital não encontrado")
    
    # Verificar se já existe quarto com o mesmo número
    db_quarto = db.query(models.Quarto).filter(models.Quarto.numero == quarto.numero).first()
    if db_quarto:
        raise HTTPException(status_code=400, detail="Número de quarto já existe")
    
    db_quarto = models.Quarto(**quarto.dict())
    db.add(db_quarto)
    db.commit()
    db.refresh(db_quarto)
    return db_quarto

@app.get("/quartos/", response_model=List[schemas.Quarto])
def read_quartos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Listar todos os quartos"""
    quartos = db.query(models.Quarto).offset(skip).limit(limit).all()
    return quartos

@app.get("/quartos/{quarto_id}", response_model=schemas.Quarto)
def read_quarto(quarto_id: int, db: Session = Depends(get_db)):
    """Obter um quarto específico"""
    quarto = db.query(models.Quarto).filter(models.Quarto.id == quarto_id).first()
    if quarto is None:
        raise HTTPException(status_code=404, detail="Quarto não encontrado")
    return quarto

@app.put("/quartos/{quarto_id}", response_model=schemas.Quarto)
def update_quarto(quarto_id: int, quarto: schemas.QuartoCreate, db: Session = Depends(get_db)):
    """Atualizar um quarto"""
    db_quarto = db.query(models.Quarto).filter(models.Quarto.id == quarto_id).first()
    if db_quarto is None:
        raise HTTPException(status_code=404, detail="Quarto não encontrado")
    
    for key, value in quarto.dict().items():
        setattr(db_quarto, key, value)
    
    db.commit()
    db.refresh(db_quarto)
    return db_quarto

@app.delete("/quartos/{quarto_id}")
def delete_quarto(quarto_id: int, db: Session = Depends(get_db)):
    """Deletar um quarto"""
    db_quarto = db.query(models.Quarto).filter(models.Quarto.id == quarto_id).first()
    if db_quarto is None:
        raise HTTPException(status_code=404, detail="Quarto não encontrado")
    
    db.delete(db_quarto)
    db.commit()
    return {"message": "Quarto deletado com sucesso"}

# ========== INTERNACAO ENDPOINTS =========
@app.post("/internacoes/", response_model=schemas.Internacao)
def create_internacao(internacao: schemas.InternacaoCreate, db: Session = Depends(get_db)):
    """Criar uma nova internação"""
    # Verificar se paciente existe
    paciente = db.query(models.Paciente).filter(models.Paciente.id == internacao.paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    
    # Verificar se médico existe
    medico = db.query(models.Medico).filter(models.Medico.id == internacao.medico_responsavel_id).first()
    if not medico:
        raise HTTPException(status_code=404, detail="Médico não encontrado")
    
    # Verificar se quarto existe
    quarto = db.query(models.Quarto).filter(models.Quarto.id == internacao.quarto_id).first()
    if not quarto:
        raise HTTPException(status_code=404, detail="Quarto não encontrado")
    
    db_internacao = models.Internacao(**internacao.dict())
    db.add(db_internacao)
    db.commit()
    db.refresh(db_internacao)
    return db_internacao

@app.get("/internacoes/", response_model=List[schemas.Internacao])
def read_internacoes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Listar todas as internações"""
    internacoes = db.query(models.Internacao).offset(skip).limit(limit).all()
    return internacoes

@app.get("/internacoes/{internacao_id}", response_model=schemas.Internacao)
def read_internacao(internacao_id: int, db: Session = Depends(get_db)):
    """Obter uma internação específica"""
    internacao = db.query(models.Internacao).filter(models.Internacao.id == internacao_id).first()
    if internacao is None:
        raise HTTPException(status_code=404, detail="Internação não encontrada")
    return internacao

@app.put("/internacoes/{internacao_id}", response_model=schemas.Internacao)
def update_internacao(internacao_id: int, internacao: schemas.InternacaoCreate, db: Session = Depends(get_db)):
    """Atualizar uma internação"""
    db_internacao = db.query(models.Internacao).filter(models.Internacao.id == internacao_id).first()
    if db_internacao is None:
        raise HTTPException(status_code=404, detail="Internação não encontrada")
    
    for key, value in internacao.dict().items():
        setattr(db_internacao, key, value)
    
    db.commit()
    db.refresh(db_internacao)
    return db_internacao

@app.delete("/internacoes/{internacao_id}")
def delete_internacao(internacao_id: int, db: Session = Depends(get_db)):
    """Deletar uma internação"""
    db_internacao = db.query(models.Internacao).filter(models.Internacao.id == internacao_id).first()
    if db_internacao is None:
        raise HTTPException(status_code=404, detail="Internação não encontrada")
    
    db.delete(db_internacao)
    db.commit()
    return {"message": "Internação deletada com sucesso"}

# ========== PRESCRICAO MEDICA ENDPOINTS =========
@app.post("/prescricoes/", response_model=schemas.PrescricaoMedica)
def create_prescricao(prescricao: schemas.PrescricaoMedicaCreate, db: Session = Depends(get_db)):
    """Criar uma nova prescrição médica"""
    # Verificar se paciente existe
    paciente = db.query(models.Paciente).filter(models.Paciente.id == prescricao.paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    
    # Verificar se médico existe
    medico = db.query(models.Medico).filter(models.Medico.id == prescricao.medico_id).first()
    if not medico:
        raise HTTPException(status_code=404, detail="Médico não encontrado")
    
    # Criar prescrição sem os medicamentos primeiro
    prescricao_data = prescricao.dict()
    medicamentos_ids = prescricao_data.pop('medicamentos_ids', [])
    
    db_prescricao = models.PrescricaoMedica(**prescricao_data)
    db.add(db_prescricao)
    db.commit()
    db.refresh(db_prescricao)
    
    # Adicionar medicamentos à prescrição se fornecidos
    if medicamentos_ids:
        medicamentos = db.query(models.Medicamento).filter(models.Medicamento.id.in_(medicamentos_ids)).all()
        db_prescricao.medicamentos.extend(medicamentos)
        db.commit()
        db.refresh(db_prescricao)
    
    return db_prescricao

@app.get("/prescricoes/", response_model=List[schemas.PrescricaoMedica])
def read_prescricoes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Listar todas as prescrições médicas"""
    prescricoes = db.query(models.PrescricaoMedica).offset(skip).limit(limit).all()
    return prescricoes

@app.get("/prescricoes/{prescricao_id}", response_model=schemas.PrescricaoMedica)
def read_prescricao(prescricao_id: int, db: Session = Depends(get_db)):
    """Obter uma prescrição médica específica"""
    prescricao = db.query(models.PrescricaoMedica).filter(models.PrescricaoMedica.id == prescricao_id).first()
    if prescricao is None:
        raise HTTPException(status_code=404, detail="Prescrição não encontrada")
    return prescricao

@app.put("/prescricoes/{prescricao_id}", response_model=schemas.PrescricaoMedica)
def update_prescricao(prescricao_id: int, prescricao: schemas.PrescricaoMedicaCreate, db: Session = Depends(get_db)):
    """Atualizar uma prescrição médica"""
    db_prescricao = db.query(models.PrescricaoMedica).filter(models.PrescricaoMedica.id == prescricao_id).first()
    if db_prescricao is None:
        raise HTTPException(status_code=404, detail="Prescrição não encontrada")
    
    for key, value in prescricao.dict().items():
        setattr(db_prescricao, key, value)
    
    db.commit()
    db.refresh(db_prescricao)
    return db_prescricao

@app.delete("/prescricoes/{prescricao_id}")
def delete_prescricao(prescricao_id: int, db: Session = Depends(get_db)):
    """Deletar uma prescrição médica"""
    db_prescricao = db.query(models.PrescricaoMedica).filter(models.PrescricaoMedica.id == prescricao_id).first()
    if db_prescricao is None:
        raise HTTPException(status_code=404, detail="Prescrição não encontrada")
    
    db.delete(db_prescricao)
    db.commit()
    return {"message": "Prescrição deletada com sucesso"}

# ========== FARMACIA ENDPOINTS =========
@app.post("/farmacias/", response_model=schemas.Farmacia)
def create_farmacia(farmacia: schemas.FarmaciaCreate, db: Session = Depends(get_db)):
    """Criar uma nova farmácia"""
    # Verificar se o hospital existe
    hospital = db.query(models.Hospital).filter(models.Hospital.id == farmacia.hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital não encontrado")
    
    db_farmacia = models.Farmacia(**farmacia.dict())
    db.add(db_farmacia)
    db.commit()
    db.refresh(db_farmacia)
    return db_farmacia

@app.get("/farmacias/", response_model=List[schemas.Farmacia])
def read_farmacias(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Listar todas as farmácias"""
    farmacias = db.query(models.Farmacia).offset(skip).limit(limit).all()
    return farmacias

@app.get("/farmacias/{farmacia_id}", response_model=schemas.Farmacia)
def read_farmacia(farmacia_id: int, db: Session = Depends(get_db)):
    """Obter uma farmácia específica"""
    farmacia = db.query(models.Farmacia).filter(models.Farmacia.id == farmacia_id).first()
    if farmacia is None:
        raise HTTPException(status_code=404, detail="Farmácia não encontrada")
    return farmacia

@app.put("/farmacias/{farmacia_id}", response_model=schemas.Farmacia)
def update_farmacia(farmacia_id: int, farmacia: schemas.FarmaciaCreate, db: Session = Depends(get_db)):
    """Atualizar uma farmácia"""
    db_farmacia = db.query(models.Farmacia).filter(models.Farmacia.id == farmacia_id).first()
    if db_farmacia is None:
        raise HTTPException(status_code=404, detail="Farmácia não encontrada")
    
    for key, value in farmacia.dict().items():
        setattr(db_farmacia, key, value)
    
    db.commit()
    db.refresh(db_farmacia)
    return db_farmacia

@app.delete("/farmacias/{farmacia_id}")
def delete_farmacia(farmacia_id: int, db: Session = Depends(get_db)):
    """Deletar uma farmácia"""
    db_farmacia = db.query(models.Farmacia).filter(models.Farmacia.id == farmacia_id).first()
    if db_farmacia is None:
        raise HTTPException(status_code=404, detail="Farmácia não encontrada")
    
    db.delete(db_farmacia)
    db.commit()
    return {"message": "Farmácia deletada com sucesso"}

# ========== MEDICAMENTO ENDPOINTS =========
@app.post("/medicamentos/", response_model=schemas.Medicamento)
def create_medicamento(medicamento: schemas.MedicamentoCreate, db: Session = Depends(get_db)):
    """Criar um novo medicamento"""
    # Verificar se a farmácia existe
    farmacia = db.query(models.Farmacia).filter(models.Farmacia.id == medicamento.farmacia_id).first()
    if not farmacia:
        raise HTTPException(status_code=404, detail="Farmácia não encontrada")
    
    db_medicamento = models.Medicamento(**medicamento.dict())
    db.add(db_medicamento)
    db.commit()
    db.refresh(db_medicamento)
    return db_medicamento

@app.get("/medicamentos/", response_model=List[schemas.Medicamento])
def read_medicamentos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Listar todos os medicamentos"""
    medicamentos = db.query(models.Medicamento).offset(skip).limit(limit).all()
    return medicamentos

@app.get("/medicamentos/{medicamento_id}", response_model=schemas.Medicamento)
def read_medicamento(medicamento_id: int, db: Session = Depends(get_db)):
    """Obter um medicamento específico"""
    medicamento = db.query(models.Medicamento).filter(models.Medicamento.id == medicamento_id).first()
    if medicamento is None:
        raise HTTPException(status_code=404, detail="Medicamento não encontrado")
    return medicamento

@app.put("/medicamentos/{medicamento_id}", response_model=schemas.Medicamento)
def update_medicamento(medicamento_id: int, medicamento: schemas.MedicamentoCreate, db: Session = Depends(get_db)):
    """Atualizar um medicamento"""
    db_medicamento = db.query(models.Medicamento).filter(models.Medicamento.id == medicamento_id).first()
    if db_medicamento is None:
        raise HTTPException(status_code=404, detail="Medicamento não encontrado")
    
    for key, value in medicamento.dict().items():
        setattr(db_medicamento, key, value)
    
    db.commit()
    db.refresh(db_medicamento)
    return db_medicamento

@app.delete("/medicamentos/{medicamento_id}")
def delete_medicamento(medicamento_id: int, db: Session = Depends(get_db)):
    """Deletar um medicamento"""
    db_medicamento = db.query(models.Medicamento).filter(models.Medicamento.id == medicamento_id).first()
    if db_medicamento is None:
        raise HTTPException(status_code=404, detail="Medicamento não encontrado")
    
    db.delete(db_medicamento)
    db.commit()
    return {"message": "Medicamento deletado com sucesso"}

# ========== CONTA HOSPITALAR ENDPOINTS =========
@app.post("/contas/", response_model=schemas.ContaHospitalar)
def create_conta(conta: schemas.ContaHospitalarCreate, db: Session = Depends(get_db)):
    """Criar uma nova conta hospitalar"""
    db_conta = models.ContaHospitalar(**conta.dict())
    db.add(db_conta)
    db.commit()
    db.refresh(db_conta)
    return db_conta

@app.get("/contas/", response_model=List[schemas.ContaHospitalar])
def read_contas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Listar todas as contas hospitalares"""
    contas = db.query(models.ContaHospitalar).offset(skip).limit(limit).all()
    return contas

@app.get("/contas/{conta_id}", response_model=schemas.ContaHospitalar)
def read_conta(conta_id: int, db: Session = Depends(get_db)):
    """Obter uma conta hospitalar específica"""
    conta = db.query(models.ContaHospitalar).filter(models.ContaHospitalar.id == conta_id).first()
    if conta is None:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    return conta

@app.put("/contas/{conta_id}", response_model=schemas.ContaHospitalar)
def update_conta(conta_id: int, conta: schemas.ContaHospitalarCreate, db: Session = Depends(get_db)):
    """Atualizar uma conta hospitalar"""
    db_conta = db.query(models.ContaHospitalar).filter(models.ContaHospitalar.id == conta_id).first()
    if db_conta is None:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    
    for key, value in conta.dict().items():
        setattr(db_conta, key, value)
    
    db.commit()
    db.refresh(db_conta)
    return db_conta

@app.delete("/contas/{conta_id}")
def delete_conta(conta_id: int, db: Session = Depends(get_db)):
    """Deletar uma conta hospitalar"""
    db_conta = db.query(models.ContaHospitalar).filter(models.ContaHospitalar.id == conta_id).first()
    if db_conta is None:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    
    db.delete(db_conta)
    db.commit()
    return {"message": "Conta deletada com sucesso"}