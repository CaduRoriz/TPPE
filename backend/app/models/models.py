from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Date, Float, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

# Tabela de associação para relacionamento many-to-many entre PrescricaoMedica e Medicamento
prescricao_medicamentos = Table(
    'prescricao_medicamentos',
    Base.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),  # Adicionando ID próprio
    Column('prescricao_id', Integer, ForeignKey('prescricoes_medicas.id', ondelete='CASCADE'), nullable=False),
    Column('medicamento_id', Integer, ForeignKey('medicamentos.id', ondelete='CASCADE'), nullable=False),
    Column('dosagem', String(100), nullable=False),
    Column('frequencia', String(100), nullable=False),
    Column('duracao', String(50), nullable=True),
    Column('observacoes', String(500), nullable=True),
    # Adicionar índice único para evitar duplicatas
    # UniqueConstraint('prescricao_id', 'medicamento_id', name='uq_prescricao_medicamento')
)

class Paciente(Base):
    __tablename__ = "pacientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    cpf = Column(String(11), nullable=False, unique=True)
    data_nascimento = Column(Date, nullable=False)
    status_saude = Column(String(100), nullable=False)
    hospital_id = Column(Integer, ForeignKey("hospitais.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    hospital = relationship("Hospital", back_populates="pacientes")
    prescricoes = relationship("PrescricaoMedica", back_populates="paciente")
    historico_internacoes = relationship("Internacao", back_populates="paciente")


class PrescricaoMedica(Base):
    __tablename__ = "prescricoes_medicas"

    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False)
    medico_id = Column(Integer, ForeignKey("medicos.id"), nullable=False)
    data = Column(Date, nullable=False)
    observacoes_clinicas = Column(String(1000), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    paciente = relationship("Paciente", back_populates="prescricoes")
    medico = relationship("Medico", back_populates="prescricoes")
    medicamentos = relationship("Medicamento", secondary=prescricao_medicamentos, back_populates="prescricoes")


class Medico(Base):
    __tablename__ = "medicos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    crm = Column(String(20), nullable=False, unique=True)
    especialidade = Column(String(100), nullable=False)
    hospital_id = Column(Integer, ForeignKey("hospitais.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    hospital = relationship("Hospital", back_populates="medicos")
    prescricoes = relationship("PrescricaoMedica", back_populates="medico")
    internacoes_responsaveis = relationship("Internacao", back_populates="medico_responsavel")


class Quarto(Base):
    __tablename__ = "quartos"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(10), nullable=False, unique=True)
    tipo = Column(String(50), nullable=False)
    capacidade = Column(Integer, nullable=False)
    valor_diario = Column(Float, nullable=False, default=0.0)
    hospital_id = Column(Integer, ForeignKey("hospitais.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    hospital = relationship("Hospital", back_populates="quartos")
    internacoes_ativas = relationship("Internacao", back_populates="quarto")


class Internacao(Base):
    __tablename__ = "internacoes"

    id = Column(Integer, primary_key=True, index=True)
    data_entrada = Column(Date, nullable=False)
    data_alta = Column(Date, nullable=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False)
    medico_responsavel_id = Column(Integer, ForeignKey("medicos.id"), nullable=False)
    quarto_id = Column(Integer, ForeignKey("quartos.id"), nullable=False)

    # Relacionamentos
    paciente = relationship("Paciente", back_populates="historico_internacoes")
    medico_responsavel = relationship("Medico", back_populates="internacoes_responsaveis")
    quarto = relationship("Quarto", back_populates="internacoes_ativas")


class Farmacia(Base):
    __tablename__ = "farmacias"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    responsavel = Column(String(100), nullable=False)
    telefone = Column(String(20), nullable=True)
    hospital_id = Column(Integer, ForeignKey("hospitais.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    hospital = relationship("Hospital", back_populates="farmacia")
    medicamentos = relationship("Medicamento", back_populates="farmacia")


class Medicamento(Base):
    __tablename__ = "medicamentos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(200), nullable=False)
    principio_ativo = Column(String(200), nullable=False)
    fabricante = Column(String(100), nullable=False)
    lote = Column(String(50), nullable=False)
    data_validade = Column(Date, nullable=False)
    quantidade_estoque = Column(Integer, nullable=False, default=0)
    preco_unitario = Column(Float, nullable=True)
    farmacia_id = Column(Integer, ForeignKey("farmacias.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    farmacia = relationship("Farmacia", back_populates="medicamentos")
    prescricoes = relationship("PrescricaoMedica", secondary=prescricao_medicamentos, back_populates="medicamentos")


class ContaHospitalar(Base):
    __tablename__ = "contas_hospitalares"

    id = Column(Integer, primary_key=True, index=True)
    total = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Hospital(Base):
    __tablename__ = "hospitais"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    endereco = Column(String(200), nullable=False)
    telefone = Column(String(20), nullable=True)
    cnpj = Column(String(14), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    pacientes = relationship("Paciente", back_populates="hospital")
    medicos = relationship("Medico", back_populates="hospital")
    quartos = relationship("Quarto", back_populates="hospital")
    farmacia = relationship("Farmacia", back_populates="hospital", uselist=False)

