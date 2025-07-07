from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime

# Schemas para Hospital
class HospitalBase(BaseModel):
    nome: str
    endereco: str
    telefone: Optional[str] = None
    cnpj: str

class HospitalCreate(HospitalBase):
    pass

class Hospital(HospitalBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Schemas para Paciente
class PacienteBase(BaseModel):
    nome: str
    cpf: str
    data_nascimento: date
    status_saude: str
    hospital_id: int

class PacienteCreate(PacienteBase):
    pass

class Paciente(PacienteBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Schemas para Medico
class MedicoBase(BaseModel):
    nome: str
    crm: str
    especialidade: str
    hospital_id: int

class MedicoCreate(MedicoBase):
    pass

class Medico(MedicoBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Schemas para Quarto
class QuartoBase(BaseModel):
    numero: str
    tipo: str
    capacidade: int
    valor_diario: float
    hospital_id: int

class QuartoCreate(QuartoBase):
    pass

class Quarto(QuartoBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Schemas para Internacao
class InternacaoBase(BaseModel):
    data_entrada: date
    data_alta: Optional[date] = None
    paciente_id: int
    medico_responsavel_id: int
    quarto_id: int

class InternacaoCreate(InternacaoBase):
    pass

class Internacao(InternacaoBase):
    id: int
    
    class Config:
        from_attributes = True

# Schemas para PrescricaoMedica  
class PrescricaoMedicaBase(BaseModel):
    data: date
    observacoes_clinicas: Optional[str] = None
    paciente_id: int
    medico_id: int

class PrescricaoMedicaCreate(PrescricaoMedicaBase):
    medicamentos_ids: List[int] = []  # Lista de IDs dos medicamentos

class MedicamentoPrescricao(BaseModel):
    """Schema para medicamento dentro de uma prescrição"""
    id: int
    nome: str
    principio_ativo: str
    dosagem: Optional[str] = None
    frequencia: Optional[str] = None
    duracao: Optional[str] = None
    observacoes: Optional[str] = None

class PrescricaoMedica(PrescricaoMedicaBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    medicamentos: List[MedicamentoPrescricao] = []
    
    class Config:
        from_attributes = True

# Schemas para Farmacia
class FarmaciaBase(BaseModel):
    nome: str
    responsavel: str
    telefone: Optional[str] = None
    hospital_id: int

class FarmaciaCreate(FarmaciaBase):
    pass

class Farmacia(FarmaciaBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Schemas para Medicamento
class MedicamentoBase(BaseModel):
    nome: str
    principio_ativo: str
    fabricante: str
    lote: str
    data_validade: date
    quantidade_estoque: int = 0
    preco_unitario: Optional[float] = None
    farmacia_id: int

class MedicamentoCreate(MedicamentoBase):
    pass

class Medicamento(MedicamentoBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Schemas para ContaHospitalar
class ContaHospitalarBase(BaseModel):
    total: float = 0.0

class ContaHospitalarCreate(ContaHospitalarBase):
    pass

class ContaHospitalar(ContaHospitalarBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True