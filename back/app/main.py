import os
from typing import List, Optional
from uuid import UUID
from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
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
from app.ai_services import (
    transcrever_audio,
    gerar_pergunta_inicial,
    gerar_proxima_pergunta,
    gerar_audio_voz,
    avaliar_entrevista_completa
)
from app.storage_helper import upload_audio_to_supabase

app = FastAPI(
    title="VoiceMatchAi API",
    description="Backend para gerenciamento de vagas e entrevistas por áudio com análise de perfil comportamental.",
    version="1.0.0"
)

# CORS Configuration
# Adjust origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development
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

        recrutador_data = {
            "id": pessoa_id,
            "empresa": data.empresa,
            "cargo": data.cargo
        }
        res_recrutador = db.table("recrutador").insert(recrutador_data).execute()
        if not res_recrutador.data:
            db.table("pessoa").delete().eq("id", pessoa_id).execute()
            raise HTTPException(status_code=400, detail="Erro ao criar registro do recrutador.")

        recrutador_obj = res_recrutador.data[0]
        recrutador_obj["pessoa"] = res_pessoa.data[0]
        return recrutador_obj

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Erro interno no servidor: {str(e)}")


# ==========================================
# Candidatos Endpoints
# ==========================================

@app.post("/candidatos", response_model=CandidatoResponse, status_code=status.HTTP_201_CREATED)
def criar_candidato(data: CandidatoRegister, db: Client = Depends(get_db)):
    try:
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

        candidato_data = {
            "id": pessoa_id,
            "curriculo_url": data.curriculo_url,
            "resumo_profissional": data.resumo_profissional,
            "experiencias": data.experiencias,
            "tecnologias": data.tecnologias
        }
        res_candidato = db.table("candidato").insert(candidato_data).execute()
        if not res_candidato.data:
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
        existing = db.table("entrevista")\
            .select("*")\
            .eq("vaga_id", str(data.vaga_id))\
            .eq("candidato_id", str(data.candidato_id))\
            .execute()
        
        if existing.data:
            return existing.data[0]

        entrevista_data = {
            "vaga_id": str(data.vaga_id),
            "candidato_id": str(data.candidato_id),
            "status": "em andamento",
            "data_inicio": "now()"
        }
        res = db.table("entrevista").insert(entrevista_data).execute()
        if not res.data:
            raise HTTPException(status_code=400, detail="Erro ao iniciar entrevista.")
        
        try:
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


# ==========================================
# Pipeline de Áudio e IA Direto na Web
# ==========================================

MAX_QUESTIONS = 5  # Número máximo de rodadas de perguntas da entrevista

@app.post("/entrevistas/{entrevista_id}/iniciar-chat", response_model=InteracaoEntrevistaResponse)
def iniciar_chat_entrevista(entrevista_id: UUID, db: Client = Depends(get_db)):
    """
    Gera a 1ª pergunta, gera a voz correspondente e salva a primeira interação na entrevista.
    """
    try:
        # 1. Verifica se já existe uma interação de ordem 1 para esta entrevista
        existing = db.table("interacao_entrevista")\
            .select("*")\
            .eq("entrevista_id", str(entrevista_id))\
            .eq("ordem", 1)\
            .execute()
            
        if existing.data:
            return existing.data[0]
            
        # 2. Busca informações da vaga associada à entrevista
        entrevista_res = db.table("entrevista").select("vaga_id").eq("id", str(entrevista_id)).execute()
        if not entrevista_res.data:
            raise HTTPException(status_code=404, detail="Entrevista não encontrada.")
        vaga_id = entrevista_res.data[0]["vaga_id"]
        
        vaga_res = db.table("vaga").select("titulo, descricao").eq("id", vaga_id).execute()
        vaga_titulo = "Vaga"
        vaga_desc = ""
        if vaga_res.data:
            vaga_titulo = vaga_res.data[0].get("titulo", "Vaga")
            vaga_desc = vaga_res.data[0].get("descricao", "")
            
        # 3. Roda IA para gerar a primeira pergunta
        pergunta_texto = gerar_pergunta_inicial(vaga_titulo, vaga_desc)
        
        # 4. Converte a pergunta em áudio (TTS) via ElevenLabs
        audio_bytes = gerar_audio_voz(pergunta_texto)
        
        # 5. Salva o áudio no Supabase Storage
        file_name = f"pergunta_1_{entrevista_id}.mp3"
        audio_url = upload_audio_to_supabase(audio_bytes, file_name)
        
        # 6. Registra no banco
        interacao_data = {
            "entrevista_id": str(entrevista_id),
            "ordem": 1,
            "pergunta_texto": pergunta_texto,
            "pergunta_audio_url": audio_url,
            "data_registro": "now()"
        }
        
        res = db.table("interacao_entrevista").insert(interacao_data).execute()
        if not res.data:
            raise HTTPException(status_code=400, detail="Erro ao salvar a primeira pergunta da entrevista.")
            
        return res.data[0]
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Erro ao iniciar o chat da entrevista: {str(e)}")


@app.post("/entrevistas/{entrevista_id}/interacoes/{interacao_id}/responder")
async def responder_interacao(
    entrevista_id: UUID, 
    interacao_id: UUID, 
    audio_file: UploadFile = File(...), 
    db: Client = Depends(get_db)
):
    """
    Recebe a resposta em áudio do candidato, transcreve com Whisper, atualiza a interação atual
    e gera a próxima pergunta (ou avalia e encerra se chegarmos no limite).
    """
    temp_file_path = f"temp_{interacao_id}.webm"
    try:
        # 1. Verifica se a interação existe e pertence à entrevista
        interacao_res = db.table("interacao_entrevista")\
            .select("*")\
            .eq("id", str(interacao_id))\
            .eq("entrevista_id", str(entrevista_id))\
            .execute()
            
        if not interacao_res.data:
            raise HTTPException(status_code=404, detail="Rodada de interação não encontrada.")
        
        interacao_atual = interacao_res.data[0]
        ordem_atual = interacao_atual["ordem"]
        
        # 2. Lê e faz upload do áudio da resposta para o Supabase Storage
        audio_bytes = await audio_file.read()
        candidato_audio_url = upload_audio_to_supabase(
            audio_bytes, 
            f"resposta_{interacao_id}_{entrevista_id}.webm"
        )
        
        # 3. Transcreve o áudio localmente via Whisper
        with open(temp_file_path, "wb") as f:
            f.write(audio_bytes)
            
        resposta_transcrita = transcrever_audio(temp_file_path)
        
        # Limpa arquivo temporário
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            
        # 4. Atualiza a interação atual com a resposta
        db.table("interacao_entrevista")\
            .update({
                "resposta_texto": resposta_transcrita,
                "resposta_audio_url": candidato_audio_url,
                "status_audio": "valido",
                "duracao_audio_segundos": 15  # Estático ou calculado no front
            })\
            .eq("id", str(interacao_id))\
            .execute()
            
        # 5. Obtém histórico de toda a entrevista para formular a próxima ação da IA
        historico_res = db.table("interacao_entrevista")\
            .select("*")\
            .eq("entrevista_id", str(entrevista_id))\
            .order("ordem")\
            .execute()
            
        historico = []
        for inter in historico_res.data:
            historico.append({"autor": "ia", "conteudo": inter["pergunta_texto"]})
            if inter.get("resposta_texto"):
                historico.append({"autor": "candidato", "conteudo": inter["resposta_texto"]})

        # Busca detalhes da vaga
        entrevista_res = db.table("entrevista").select("vaga_id, candidato_id").eq("id", str(entrevista_id)).execute()
        vaga_id = entrevista_res.data[0]["vaga_id"]
        candidato_id = entrevista_res.data[0]["candidato_id"]
        vaga_res = db.table("vaga").select("titulo, descricao").eq("id", vaga_id).execute()
        vaga_info = f"Vaga: {vaga_res.data[0]['titulo']}. Descrição: {vaga_res.data[0]['descricao']}" if vaga_res.data else ""

        # 6. Avalia se a entrevista encerra ou continua
        if ordem_atual >= MAX_QUESTIONS:
            # --- FINALIZAR E AVALIAR ENTREVISTA ---
            avaliacao = avaliar_entrevista_completa(historico, vaga_info)
            
            # Atualiza entrevista
            feedback_ia = (
                f"Pontos Fortes:\n" + "\n".join([f"- {p}" for p in avaliacao["pontosFortes"]]) + "\n\n"
                f"Pontos a Desenvolver:\n" + "\n".join([f"- {p}" for p in avaliacao["pontosFracos"]])
            )
            db.table("entrevista")\
                .update({
                    "status": "concluída",
                    "data_fim": "now()",
                    "score_geral": avaliacao["notaFinal"],
                    "feedback_recrutador": feedback_ia
                })\
                .eq("id", str(entrevista_id))\
                .execute()
                
            # Atualiza tabela candidato com o perfil comportamental avaliado
            db.table("candidato")\
                .update({
                    "perfil_avaliado": avaliacao["perfilAvaliado"],
                    "nota_final": avaliacao["notaFinal"],
                    "pontos_fortes": avaliacao["pontosFortes"],
                    "pontos_fracos": avaliacao["pontosFracos"],
                    "melhorias": avaliacao["melhorias"]
                })\
                .eq("id", candidato_id)\
                .execute()
                
            return {
                "finalizada": True,
                "nota_final": avaliacao["notaFinal"],
                "mensagem": "Entrevista concluída com sucesso. Obrigado!"
            }
            
        else:
            # --- CONTINUAR: GERAR PRÓXIMA PERGUNTA ---
            proxima_ordem = ordem_atual + 1
            proxima_pergunta = gerar_proxima_pergunta(historico, vaga_info)
            
            # TTS
            audio_bytes = gerar_audio_voz(proxima_pergunta)
            proxima_pergunta_audio_url = upload_audio_to_supabase(
                audio_bytes, 
                f"pergunta_{proxima_ordem}_{entrevista_id}.mp3"
            )
            
            # Insere nova interação limpa aguardando resposta
            nova_interacao_data = {
                "entrevista_id": str(entrevista_id),
                "ordem": proxima_ordem,
                "pergunta_texto": proxima_pergunta,
                "pergunta_audio_url": proxima_pergunta_audio_url,
                "data_registro": "now()"
            }
            res_nova = db.table("interacao_entrevista").insert(nova_interacao_data).execute()
            
            return {
                "finalizada": False,
                "proxima_interacao": res_nova.data[0]
            }

    except Exception as e:
        # Certifica-se de remover arquivo local de áudio se der erro
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Erro ao processar resposta da interação: {str(e)}")
