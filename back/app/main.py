from typing import List, Optional
from uuid import UUID
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from supabase import Client

from app.models import (
    PessoaResponse,
    RecrutadorRegister,
    RecrutadorResponse,
    CandidatoRegister,
    CandidatoResponse,
    VagaCreate,
    VagaResponse,
    EntrevistaCreate,
    EntrevistaResponse,
    InteracaoEntrevistaCreate,
    InteracaoEntrevistaResponse,
    StatusEntrevistaEnum
)
from app.supabase_client import get_supabase_client

app = FastAPI(
    title="VoiceMatchAi API",
    description="Backend para gerenciamento de vagas e entrevistas por áudio com análise de perfil comportamental.",
    version="1.0.0"
)

# CORS Configuration
# Adjust origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development (front is on localhost:3000)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency to get Supabase client and check availability
def get_db() -> Client:
    try:
        return get_supabase_client()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Banco de dados Supabase indisponível ou não configurado no .env. Detalhes: {str(e)}"
        )


@app.get("/")
def read_root():
    return {
        "status": "online",
        "api": "VoiceMatchAi",
        "message": "Backend rodando com sucesso. Acesse /docs para a documentação Swagger."
    }


# ==========================================
# Recrutadores Endpoints
# ==========================================

@app.post("/recrutadores", response_model=RecrutadorResponse, status_code=status.HTTP_201_CREATED)
def criar_recrutador(data: RecrutadorRegister, db: Client = Depends(get_db)):
    try:
        # 1. Create entry in table 'pessoa'
        pessoa_data = {
            "nome_completo": data.nome_completo,
            "email": data.email,
            "telefone": data.telefone,
            "cpf": data.cpf,
            "tipo_usuario": "recrutador"
        }
        res_pessoa = db.table("pessoa").insert(pessoa_data).execute()
        if not res_pessoa.data:
            raise HTTPException(status_code=400, detail="Erro ao criar registro da pessoa.")
        
        pessoa_id = res_pessoa.data[0]["id"]

        # 2. Create entry in table 'recrutador'
        recrutador_data = {
            "id": pessoa_id,
            "empresa": data.empresa,
            "cargo": data.cargo
        }
        res_recrutador = db.table("recrutador").insert(recrutador_data).execute()
        if not res_recrutador.data:
            # Cleanup person if recruiter creation fails
            db.table("pessoa").delete().eq("id", pessoa_id).execute()
            raise HTTPException(status_code=400, detail="Erro ao criar registro do recrutador.")

        recrutador_obj = res_recrutador.data[0]
        recrutador_obj["pessoa"] = res_pessoa.data[0]
        return recrutador_obj

    except Exception as e:
        # Check if it's already an HTTPException
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Erro interno no servidor: {str(e)}")


# ==========================================
# Candidatos Endpoints
# ==========================================

@app.post("/candidatos", response_model=CandidatoResponse, status_code=status.HTTP_201_CREATED)
def criar_candidato(data: CandidatoRegister, db: Client = Depends(get_db)):
    try:
        # 1. Create entry in table 'pessoa'
        pessoa_data = {
            "nome_completo": data.nome_completo,
            "email": data.email,
            "telefone": data.telefone,
            "cpf": data.cpf,
            "tipo_usuario": "candidato"
        }
        res_pessoa = db.table("pessoa").insert(pessoa_data).execute()
        if not res_pessoa.data:
            raise HTTPException(status_code=400, detail="Erro ao criar registro da pessoa.")
        
        pessoa_id = res_pessoa.data[0]["id"]

        # 2. Create entry in table 'candidato'
        candidato_data = {
            "id": pessoa_id,
            "curriculo_url": data.curriculo_url,
            "resumo_profissional": data.resumo_profissional,
            "experiencias": data.experiencias,
            "tecnologias": data.tecnologias
        }
        res_candidato = db.table("candidato").insert(candidato_data).execute()
        if not res_candidato.data:
            # Cleanup person if candidate creation fails
            db.table("pessoa").delete().eq("id", pessoa_id).execute()
            raise HTTPException(status_code=400, detail="Erro ao criar registro do candidato.")

        candidato_obj = res_candidato.data[0]
        candidato_obj["pessoa"] = res_pessoa.data[0]
        return candidato_obj

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Erro interno no servidor: {str(e)}")


@app.get("/candidatos", response_model=List[CandidatoResponse])
def listar_candidatos(db: Client = Depends(get_db)):
    try:
        # Fetch candidates and join with pessoa
        # Supabase allows joins using relationship notation
        res = db.table("candidato").select("*, pessoa(*)").execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar candidatos: {str(e)}")


@app.get("/candidatos/{id}", response_model=CandidatoResponse)
def obter_candidato(id: UUID, db: Client = Depends(get_db)):
    try:
        res = db.table("candidato").select("*, pessoa(*)").eq("id", str(id)).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Candidato não encontrado.")
        return res.data[0]
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Erro ao obter candidato: {str(e)}")


# ==========================================
# Vagas Endpoints
# ==========================================

@app.get("/vagas", response_model=List[VagaResponse])
def listar_vagas(db: Client = Depends(get_db)):
    try:
        res = db.table("vaga").select("*").execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar vagas: {str(e)}")


@app.get("/vagas/{id}", response_model=VagaResponse)
def obter_vaga(id: UUID, db: Client = Depends(get_db)):
    try:
        res = db.table("vaga").select("*").eq("id", str(id)).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Vaga não encontrada.")
        return res.data[0]
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Erro ao buscar vaga: {str(e)}")


@app.post("/vagas", response_model=VagaResponse, status_code=status.HTTP_201_CREATED)
def criar_vaga(vaga: VagaCreate, db: Client = Depends(get_db)):
    try:
        res = db.table("vaga").insert(vaga.model_dump()).execute()
        if not res.data:
            raise HTTPException(status_code=400, detail="Erro ao criar vaga.")
        return res.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar vaga: {str(e)}")


# ==========================================
# Entrevistas Endpoints
# ==========================================

@app.post("/entrevistas/iniciar", response_model=EntrevistaResponse, status_code=status.HTTP_201_CREATED)
def iniciar_entrevista(data: EntrevistaCreate, db: Client = Depends(get_db)):
    try:
        # Check if interview already exists for this candidate and vacancy
        existing = db.table("entrevista")\
            .select("*")\
            .eq("vaga_id", str(data.vaga_id))\
            .eq("candidato_id", str(data.candidato_id))\
            .execute()
        
        if existing.data:
            return existing.data[0]  # Return existing interview instead of creating a duplicate

        # Create new interview
        entrevista_data = {
            "vaga_id": str(data.vaga_id),
            "candidato_id": str(data.candidato_id),
            "status": "em andamento",
            "data_inicio": "now()"  # Postgres server timestamp helper
        }
        res = db.table("entrevista").insert(entrevista_data).execute()
        if not res.data:
            raise HTTPException(status_code=400, detail="Erro ao iniciar entrevista.")
        
        # Increment number of applications (inscricoes) for the vacancy
        try:
            # Get current vagas data to fetch current inscricoes
            vaga_res = db.table("vaga").select("inscricoes").eq("id", str(data.vaga_id)).execute()
            if vaga_res.data:
                current_inscricoes = vaga_res.data[0].get("inscricoes") or 0
                db.table("vaga")\
                    .update({"inscricoes": current_inscricoes + 1})\
                    .eq("id", str(data.vaga_id))\
                    .execute()
        except Exception as e:
            print(f"[WARNING] Failed to increment vaga applications: {e}")

        return res.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao iniciar entrevista: {str(e)}")


@app.get("/entrevistas/{id}", response_model=EntrevistaResponse)
def obter_entrevista(id: UUID, db: Client = Depends(get_db)):
    try:
        res = db.table("entrevista").select("*").eq("id", str(id)).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Entrevista não encontrada.")
        return res.data[0]
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Erro ao obter entrevista: {str(e)}")


# ==========================================
# Interações Endpoints (Mensagens do Chat)
# ==========================================

@app.get("/entrevistas/{entrevista_id}/interacoes", response_model=List[InteracaoEntrevistaResponse])
def listar_interacoes(entrevista_id: UUID, db: Client = Depends(get_db)):
    try:
        res = db.table("interacao_entrevista")\
            .select("*")\
            .eq("entrevista_id", str(entrevista_id))\
            .order("ordem", desc=False)\
            .execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar interações: {str(e)}")


@app.post("/entrevistas/{entrevista_id}/interacoes", response_model=InteracaoEntrevistaResponse, status_code=status.HTTP_201_CREATED)
def criar_interacao(entrevista_id: UUID, interacao: InteracaoEntrevistaCreate, db: Client = Depends(get_db)):
    try:
        # Enforce path parameter consistency
        if interacao.entrevista_id != entrevista_id:
            raise HTTPException(
                status_code=400,
                detail="O id da entrevista no corpo da requisição deve corresponder ao da URL."
            )
            
        res = db.table("interacao_entrevista").insert(interacao.model_dump()).execute()
        if not res.data:
            raise HTTPException(status_code=400, detail="Erro ao registrar interação.")
        return res.data[0]
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Erro ao criar interação: {str(e)}")
