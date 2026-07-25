from typing import Optional
from supabase import Client
from app.supabase_client import get_supabase_client

def upload_audio_to_supabase(file_bytes: bytes, file_name: str, bucket_name: str = "entrevistas-audios") -> str:
    """
    Realiza o upload de bytes de áudio para o Supabase Storage e retorna a URL pública.
    Caso o Supabase não esteja totalmente configurado ou ocorra um erro, retorna
    uma URL simulada para não bloquear o fluxo do candidato.
    """
    try:
        # Get client
        db: Client = get_supabase_client()
        
        # Determine content type based on extension
        content_type = "audio/mpeg"
        if file_name.endswith(".webm"):
            content_type = "audio/webm"
        elif file_name.endswith(".wav"):
            content_type = "audio/wav"
            
        # Try uploading
        # Options allow upserting to overwrite if the file already exists
        db.storage.from_(bucket_name).upload(
            path=file_name,
            file=file_bytes,
            file_options={
                "content-type": content_type,
                "x-upsert": "true"
            }
        )
        
        # Retrieve the public URL
        public_url = db.storage.from_(bucket_name).get_public_url(file_name)
        return public_url
        
    except Exception as e:
        print(f"[WARNING] Supabase Storage upload failed or not configured: {e}. Using mock URL.")
        # Fallback to a placeholder URL for testing
        return f"https://www.soundhelix.com/examples/mp3/SoundHelix-Song-{random_song_number()}.mp3"


def random_song_number() -> int:
    # Retorna uma música aleatória do SoundHelix para termos um player funcional no front se mockado
    import random
    return random.randint(1, 8)
