import os
import base64
import random
import json
from typing import List, Dict, Any
import httpx
from openai import OpenAI
from app.models import Trait, PerfilComportamental

# ==========================================
# Tiny Silent MP3 Base64 (for ElevenLabs Mock)
# ==========================================
TINY_SILENT_MP3_B64 = (
    "SUQzBAAAAAAAF1RTU0UAAAANAAFEZWN1bHRyYSBNUDMA//uQZAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAGluZm8AAAAHAAAAAwAAAGQAAP/7kGQAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAFQAAAAAAAABkAAAAAP/7kGQAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAFQAAAAAAAABkAAAAAP/7kGQAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAFQAAAAAAAABkAAAAAP/7kGQAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAFQAAAAAAAABkAAAAAP/7kGQAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAFQAAAAAAAABkAAAAAP/7kGQAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAFQAAAAAAAABkAAAAA=="
)

def get_openai_client() -> Optional[OpenAI]:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key or "sua_chave" in api_key or api_key == "":
        return None
    try:
        return OpenAI(api_key=api_key)
    except Exception as e:
        print(f"[WARNING] Failed to initialize OpenAI client: {e}")
        return None

# ==========================================
# 1. Transcrição (Speech-to-Text - Whisper)
# ==========================================

def transcrever_audio(file_path: str) -> str:
    """
    Transcreve um arquivo de áudio utilizando a API do OpenAI Whisper.
    Caso a chave da API não esteja configurada, retorna uma transcrição simulada.
    """
    client = get_openai_client()
    if not client:
        print("[MOCK] OpenAI API Key não configurada. Simulando transcrição do áudio.")
        mock_answers = [
            "Gosto de trabalhar em equipe porque acredito que a diversidade de opiniões enriquece o resultado final. Em meu último projeto, ajudei a integrar desenvolvedores de diferentes áreas e conseguimos entregar a feature antes do prazo.",
            "Sim, eu tenho bastante familiaridade com React e Next.js. Trabalho com essas tecnologias há cerca de 3 anos, construindo páginas dinâmicas, integrando com APIs REST e otimizando a performance e o SEO com renderização no servidor.",
            "Quando enfrento um prazo apertado, eu primeiro priorizo as tarefas críticas que agregam mais valor. Em seguida, alinho com o time as expectativas e foco na entrega funcional do MVP, resolvendo gargalos de forma proativa.",
            "Em uma situação de conflito técnico, eu busco sempre escutar os argumentos da outra pessoa e avaliar com base em métricas e dados de teste, em vez de opiniões pessoais. Geralmente fazemos um teste A/B ou avaliamos qual solução atende melhor aos requisitos do cliente.",
            "Meu processo de aprendizado envolve bastante prática. Eu costumo ler a documentação oficial da ferramenta, criar um pequeno projeto de teste (pet project) para entender as limitações e, se possível, compartilhar o que aprendi com o time."
        ]
        return random.choice(mock_answers)

    try:
        with open(file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            return transcript.text
    except Exception as e:
        print(f"[ERROR] Erro na transcrição real do Whisper: {e}. Usando mock.")
        return "Desculpe, ocorreu um erro no processamento do seu áudio, mas tenho muito interesse na vaga."


# ==========================================
# 2. Geração de Perguntas (GPT-4o)
# ==========================================

def gerar_pergunta_inicial(vaga_titulo: str, descricao: str) -> str:
    """
    Gera a primeira pergunta da entrevista com base nos requisitos da vaga.
    """
    client = get_openai_client()
    if not client:
        print("[MOCK] OpenAI API Key não configurada. Usando pergunta inicial padrão.")
        return f"Olá! Seja bem-vindo à entrevista virtual para a vaga de {vaga_titulo}. Para iniciarmos, você poderia se apresentar brevemente e compartilhar um pouco da sua experiência recente com as tecnologias exigidas para o cargo?"

    try:
        system_prompt = (
            "Você é uma inteligência artificial entrevistadora técnica especializada em recrutamento.\n"
            "Seu objetivo é conduzir uma entrevista profissional de forma humanizada, amigável e objetiva.\n"
            "Instruções:\n"
            "- Gere APENAS a primeira pergunta da entrevista.\n"
            "- A pergunta deve ser curta (1 a 2 frases no máximo) e natural para ser ouvida em áudio.\n"
            "- Peça para o candidato se apresentar e fale sobre a vaga mencionada."
        )
        user_prompt = f"Vaga: {vaga_titulo}\nRequisitos/Descrição: {descricao}"

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[ERROR] Erro ao gerar pergunta inicial: {e}")
        return f"Olá! Bem-vindo ao processo seletivo de {vaga_titulo}. Por favor, apresente-se e fale um pouco sobre sua trajetória profissional."


def gerar_proxima_pergunta(historico: List[Dict[str, str]], vaga_info: str) -> str:
    """
    Gera a próxima pergunta com base no histórico da entrevista (perguntas anteriores e respostas do candidato).
    """
    client = get_openai_client()
    if not client:
        print("[MOCK] OpenAI API Key não configurada. Usando próxima pergunta simulada.")
        mock_questions = [
            "Excelente. Como você costuma lidar com prazos apertados e pressões em entregas de projetos?",
            "Entendi perfeitamente. Pode me descrever uma situação onde teve um conflito técnico com um colega de equipe e como vocês resolveram isso?",
            "Muito bom. E sobre novas ferramentas ou linguagens, como é o seu processo de aprendizado quando precisa usá-las em um novo projeto?",
            "Perfeito. Pensando em melhorias contínuas, qual foi o maior desafio técnico que você superou recentemente e o que aprendeu com ele?"
        ]
        # Pick a question that wasn't asked yet (based on history length)
        # Historico has pairs of IA and Candidate messages
        question_index = min(len(historico) // 2, len(mock_questions) - 1)
        return mock_questions[question_index]

    try:
        system_prompt = (
            "Você é uma inteligência artificial entrevistadora técnica especializada em recrutamento.\n"
            "Seu objetivo é dar continuidade à entrevista de forma dinâmica.\n"
            "Instruções:\n"
            "- Avalie a última resposta do candidato e faça uma breve transição (ex: 'Entendi', 'Muito bom', 'Legal').\n"
            "- Formule a PRÓXIMA pergunta relevante.\n"
            "- A pergunta deve ser focada em soft skills, trabalho em equipe, resolução de problemas ou hard skills da vaga.\n"
            "- Seja breve: limite a pergunta a 1 ou 2 frases curtas, ideal para reprodução por voz."
        )
        
        messages = [{"role": "system", "content": system_prompt}]
        for msg in historico:
            role = "assistant" if msg["autor"] == "ia" else "user"
            messages.append({"role": role, "content": msg["conteudo"]})

        messages.append({"role": "user", "content": f"[INFORMAÇÕES DA VAGA]\n{vaga_info}\n\nPor favor, faça a próxima pergunta baseando-se no nosso histórico."})

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[ERROR] Erro ao gerar próxima pergunta: {e}")
        return "Entendi. Você poderia me dar um exemplo de projeto desafiador que você desenvolveu recentemente?"


# ==========================================
# 3. Conversão de Texto em Voz (ElevenLabs)
# ==========================================

def gerar_audio_voz(texto: str) -> bytes:
    """
    Converte um texto em áudio usando a API da ElevenLabs.
    Caso a chave da API não esteja configurada, decodifica e retorna um áudio silencioso de 1s em formato MP3.
    """
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    voice_id = os.environ.get("ELEVENLABS_VOICE_ID") or "21m00Tcm4TlvDq8ikWAM"  # Default voice Rachel

    if not api_key or "sua_chave" in api_key or api_key == "":
        print("[MOCK] ElevenLabs API Key não configurada. Gerando áudio de teste silencioso.")
        return base64.b64decode(TINY_SILENT_MP3_B64)

    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        data = {
            "text": texto,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        # Using httpx for a direct clean HTTP request
        with httpx.Client() as http_client:
            response = http_client.post(url, json=data, headers=headers, timeout=30.0)
            if response.status_code == 200:
                return response.content
            else:
                print(f"[WARNING] ElevenLabs API retornou erro {response.status_code}: {response.text}. Usando mock.")
                return base64.b64decode(TINY_SILENT_MP3_B64)
    except Exception as e:
        print(f"[ERROR] Falha na integração com ElevenLabs: {e}. Usando mock.")
        return base64.b64decode(TINY_SILENT_MP3_B64)


# ==========================================
# 4. Avaliação Comportamental Final (GPT-4o)
# ==========================================

def avaliar_entrevista_completa(historico: List[Dict[str, str]], vaga_info: str) -> Dict[str, Any]:
    """
    Avalia a transcrição completa da entrevista utilizando GPT-4o para extrair
    o score final, pontos fortes, pontos fracos, melhorias e o radar com os 20 traços comportamentais.
    """
    client = get_openai_client()
    
    # 20 traits mapped from types.ts / models.py
    traits_list = [
        "equipe", "proatividade", "resiliencia", "foco_em_resultado", "negociacao",
        "relacao_hierarquica", "resolucao_de_conflito", "inovacao", "acao_sob_pressao",
        "assertividade", "autenticidade", "autonomia", "comunicabilidade", "cuidado",
        "disciplina", "empenho", "flexibilidade", "seguranca", "tranquilidade", "vitalidade_corporal"
    ]

    if not client:
        print("[MOCK] OpenAI API Key não configurada. Gerando relatório de avaliação comportamental simulado.")
        # Generate simulated scores (between 4 and 9)
        mock_perfil = {trait: random.randint(5, 9) for trait in traits_list}
        return {
            "notaFinal": round(random.uniform(7.0, 9.2), 1),
            "pontosFortes": [
                "Comunicação clara, objetiva e estruturada.",
                "Grande orientação a trabalho colaborativo e resolução de problemas em grupo.",
                "Demonstrou proatividade em sugerir melhorias de processos."
            ],
            "pontosFracos": [
                "Pode aprofundar mais em conhecimentos técnicos de infraestrutura se a vaga exigir.",
                "Exibe alguma ansiedade ao descrever metas sob extrema pressão."
            ],
            "melhorias": [
                "Aprimorar técnicas de mediação em discussões técnicas complexas.",
                "Praticar a síntese de respostas para manter o foco em perguntas abertas."
            ],
            "perfilAvaliado": mock_perfil
        }

    try:
        system_prompt = (
            "Você é um psicólogo organizacional e especialista em atração de talentos.\n"
            "Seu trabalho é analisar o histórico da entrevista por texto de um candidato e fornecer uma avaliação detalhada.\n"
            "Você DEVE retornar a resposta EXATAMENTE no formato JSON com as seguintes chaves:\n"
            "- 'notaFinal': número de 0 a 10 representando o fit cultural/técnico do candidato.\n"
            "- 'pontosFortes': lista de strings detalhando os principais pontos fortes comportamentais.\n"
            "- 'pontosFracos': lista de strings com pontos fracos observados.\n"
            "- 'melhorias': lista de dicas de desenvolvimento profissional para o candidato.\n"
            "- 'perfilAvaliado': objeto onde as chaves são os 20 traços comportamentais específicos informados e as notas associadas de 1 a 10 (inteiro).\n\n"
            "Os 20 traços que você deve avaliar no 'perfilAvaliado' são:\n"
            f"{', '.join(traits_list)}"
        )

        user_content = (
            f"[INFORMAÇÕES DA VAGA]\n{vaga_info}\n\n"
            f"[TRANSCRIÇÃO DA ENTREVISTA]\n"
        )
        for msg in historico:
            autor = "Entrevistador" if msg["autor"] == "ia" else "Candidato"
            user_content += f"{autor}: {msg['conteudo']}\n"

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        
        result_json = json.loads(response.choices[0].message.content)
        
        # Ensure all 20 traits exist in response, fill missing with 5 as fallback
        perfil = result_json.get("perfilAvaliado", {})
        for trait in traits_list:
            if trait not in perfil:
                perfil[trait] = 5
        result_json["perfilAvaliado"] = perfil

        return result_json
        
    except Exception as e:
        print(f"[ERROR] Erro ao avaliar entrevista completa com IA: {e}. Usando mock.")
        mock_perfil = {trait: random.randint(4, 9) for trait in traits_list}
        return {
            "notaFinal": 7.0,
            "pontosFortes": ["Comunicação amigável durante a conversa."],
            "pontosFracos": ["Respostas muito curtas para avaliação aprofundada."],
            "melhorias": ["Tente fornecer exemplos mais detalhados e estruturados em futuras entrevistas."],
            "perfilAvaliado": mock_perfil
        }
