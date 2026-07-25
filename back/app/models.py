from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


# ==========================================
# Database Enums
# ==========================================

class TipoUsuarioEnum(str, Enum):
    recrutador = "recrutador"
    candidato = "candidato"


class StatusVagaEnum(str, Enum):
    ativa = "ativa"
    pausada = "pausada"
    encerrada = "encerrada"


class StatusEntrevistaEnum(str, Enum):
    agendada = "agendada"
    em_andamento = "em andamento"
    concluida = "concluída"
    cancelada = "cancelada"


class StatusAudioEnum(str, Enum):
    valido = "valido"
    invalido = "invalido"


# ==========================================
# Pessoa Models
# ==========================================

class PessoaBase(BaseModel):
    nome_completo: str
    email: EmailStr
    telefone: Optional[str] = None
    cpf: Optional[str] = None
    tipo_usuario: TipoUsuarioEnum

class PessoaCreate(PessoaBase):
    pass

class PessoaResponse(PessoaBase):
    id: UUID
    data_criacao: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==========================================
# Recrutador Models
# ==========================================

class RecrutadorBase(BaseModel):
    empresa: str
    cargo: Optional[str] = None

class RecrutadorCreate(RecrutadorBase):
    id: UUID  # Must match the Pessoa ID

class RecrutadorResponse(RecrutadorBase):
    id: UUID
    pessoa: Optional[PessoaResponse] = None

    class Config:
        from_attributes = True


class RecrutadorRegister(BaseModel):
    """Convenience model to create Pessoa and Recrutador in one go"""
    nome_completo: str
    email: EmailStr
    telefone: Optional[str] = None
    cpf: Optional[str] = None
    empresa: str
    cargo: Optional[str] = None



# ==========================================
# Candidato Models
# ==========================================

class CandidatoBase(BaseModel):
    curriculo_url: Optional[str] = None
    resumo_profissional: Optional[str] = None
    experiencias: Optional[List[Dict[str, Any]] or Dict[str, Any]] = None
    tecnologias: Optional[List[str] or Dict[str, Any]] = None

class CandidatoCreate(CandidatoBase):
    id: UUID  # Must match the Pessoa ID

class CandidatoRegister(BaseModel):
    """Convenience model to create Pessoa and Candidato in one go"""
    nome_completo: str
    email: EmailStr
    telefone: Optional[str] = None
    cpf: Optional[str] = None
    curriculo_url: Optional[str] = None
    resumo_profissional: Optional[str] = None
    experiencias: Optional[List[Dict[str, Any]]] = None
    tecnologias: Optional[List[str]] = None

class CandidatoResponse(CandidatoBase):
    id: UUID
    pessoa: Optional[PessoaResponse] = None

    class Config:
        from_attributes = True


# ==========================================
# Vaga Models
# ==========================================

class VagaBase(BaseModel):
    titulo: str
    descricao: str
    descricao_candidato_ideal: Optional[str] = None
    requisitos_hard: Optional[List[str]] = None
    requisitos_soft: Optional[List[str]] = None
    status: Optional[StatusVagaEnum] = StatusVagaEnum.ativa

class VagaCreate(VagaBase):
    recrutador_id: UUID

class VagaResponse(VagaBase):
    id: UUID
    recrutador_id: UUID
    inscricoes: Optional[int] = 0
    data_criacao: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==========================================
# Entrevista Models
# ==========================================

class EntrevistaBase(BaseModel):
    status: Optional[StatusEntrevistaEnum] = StatusEntrevistaEnum.agendada
    score_geral: Optional[float] = None
    feedback_candidato: Optional[str] = None
    feedback_recrutador: Optional[str] = None

class EntrevistaCreate(BaseModel):
    vaga_id: UUID
    candidato_id: UUID

class EntrevistaResponse(EntrevistaBase):
    id: UUID
    vaga_id: UUID
    candidato_id: UUID
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==========================================
# Interacao Entrevista Models
# ==========================================

class InteracaoEntrevistaBase(BaseModel):
    ordem: int
    pergunta_texto: str
    pergunta_audio_url: Optional[str] = None
    resposta_audio_url: Optional[str] = None
    resposta_texto: Optional[str] = None
    duracao_audio_segundos: Optional[int] = None
    status_audio: Optional[StatusAudioEnum] = None

class InteracaoEntrevistaCreate(InteracaoEntrevistaBase):
    entrevista_id: UUID

class InteracaoEntrevistaResponse(InteracaoEntrevistaBase):
    id: UUID
    entrevista_id: UUID
    data_registro: Optional[datetime] = None

    class Config:
        from_attributes = True
