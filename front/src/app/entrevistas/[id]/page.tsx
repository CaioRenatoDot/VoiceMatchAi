"use client";

import { useEffect, useState, useRef, use } from "react";
import { Mic, Play, Volume2, CheckCircle2, ChevronLeft, Loader2, Sparkles } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { Button } from "@/_components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/_components/ui/card";
import { ScrollArea } from "@/_components/ui/scroll-area";
import { AudioRecorder } from "@/_components/ui/audio-recorder";
import { toast } from "sonner";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Interacao {
  id: string;
  ordem: number;
  pergunta_texto: string;
  pergunta_audio_url: string | null;
  resposta_texto: string | null;
  resposta_audio_url: string | null;
}

interface EntrevistaInfo {
  id: string;
  status: string;
  vaga_id: string;
  candidato_id: string;
}

export default function EntrevistaChatPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id: entrevistaId } = use(params);
  const router = useRouter();

  const [loading, setLoading] = useState(true);
  const [entrevista, setEntrevista] = useState<EntrevistaInfo | null>(null);
  const [interacoes, setInteracoes] = useState<Interacao[]>([]);
  const [currentInteracao, setCurrentInteracao] = useState<Interacao | null>(null);
  const [processandoResposta, setProcessandoResposta] = useState(false);
  const [entrevistaConcluida, setEntrevistaConcluida] = useState(false);
  const [playingAudioUrl, setPlayingAudioUrl] = useState<string | null>(null);

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const scrollAreaEndRef = useRef<HTMLDivElement | null>(null);

  // Load interview details & initial state
  useEffect(() => {
    async function carregarEntrevista() {
      try {
        setLoading(true);
        // 1. Fetch current interview details
        const infoRes = await fetch(`${API_URL}/entrevistas/${entrevistaId}`);
        if (!infoRes.ok) {
          throw new Error("Entrevista não encontrada ou erro no servidor.");
        }
        const infoData = await infoRes.json();
        setEntrevista(infoData);

        if (infoData.status === "concluída") {
          setEntrevistaConcluida(true);
          setLoading(false);
          return;
        }

        // 2. Fetch existing interactions
        const interRes = await fetch(`${API_URL}/entrevistas/${entrevistaId}/interacoes`);
        const interData = await interRes.json();

        if (interData && interData.length > 0) {
          setInteracoes(interData);
          // Look for the last interaction that doesn't have a response yet
          const pending = interData.find((i: Interacao) => !i.resposta_texto);
          if (pending) {
            setCurrentInteracao(pending);
          } else {
            // If all are answered, let's wait or fetch next
            setCurrentInteracao(interData[interData.length - 1]);
          }
        } else {
          // No interactions yet, let's start the chat session (this generates question 1)
          await iniciarChat();
        }
      } catch (err: any) {
        console.error(err);
        toast.error("Erro de conexão", {
          description: "Não foi possível carregar os detalhes da entrevista do backend.",
        });
      } finally {
        setLoading(false);
      }
    }

    carregarEntrevista();
  }, [entrevistaId]);

  // Autoscroll when new messages are added
  useEffect(() => {
    if (scrollAreaEndRef.current) {
      scrollAreaEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [interacoes, processandoResposta]);

  async function iniciarChat() {
    try {
      const res = await fetch(`${API_URL}/entrevistas/${entrevistaId}/iniciar-chat`, {
        method: "POST",
      });
      if (!res.ok) throw new Error("Falha ao iniciar entrevista.");
      
      const primeiraInteracao = await res.json();
      setInteracoes([primeiraInteracao]);
      setCurrentInteracao(primeiraInteracao);
      
      // Auto-play the first question
      if (primeiraInteracao.pergunta_audio_url) {
        tocarAudio(primeiraInteracao.pergunta_audio_url);
      }
    } catch (err) {
      console.error(err);
      toast.error("Erro", { description: "Não foi possível iniciar as perguntas da IA." });
    }
  }

  function tocarAudio(url: string) {
    if (audioRef.current) {
      audioRef.current.src = url;
      audioRef.current.play()
        .then(() => setPlayingAudioUrl(url))
        .catch((e) => console.log("Erro de autoplay no navegador: ", e));
    }
  }

  async function enviarResposta(audioBlob: Blob) {
    if (!currentInteracao) return;
    
    try {
      setProcessandoResposta(true);
      
      // Create Form Data containing the audio file
      const formData = new FormData();
      formData.append("audio_file", audioBlob, `resposta_${currentInteracao.id}.webm`);
      
      // Send to responder endpoint
      const res = await fetch(
        `${API_URL}/entrevistas/${entrevistaId}/interacoes/${currentInteracao.id}/responder`,
        {
          method: "POST",
          body: formData,
        }
      );
      
      if (!res.ok) {
        throw new Error("Erro ao enviar áudio.");
      }
      
      const result = await res.json();
      
      // Fetch updated interactions to refresh chat list
      const updateRes = await fetch(`${API_URL}/entrevistas/${entrevistaId}/interacoes`);
      const updatedList = await updateRes.json();
      setInteracoes(updatedList);
      
      if (result.finalizada) {
        setEntrevistaConcluida(true);
        toast.success("Entrevista Concluída!", {
          description: "Suas respostas foram avaliadas pelo nosso modelo comportamental.",
        });
      } else {
        const proxima = result.proxima_interacao;
        setCurrentInteracao(proxima);
        
        // Auto play next question voice
        if (proxima.pergunta_audio_url) {
          tocarAudio(proxima.pergunta_audio_url);
        }
      }
    } catch (err) {
      console.error(err);
      toast.error("Erro no Envio", {
        description: "Não conseguimos transcrever ou salvar seu áudio. Tente falar novamente.",
      });
    } finally {
      setProcessandoResposta(false);
    }
  }

  if (loading) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-4 bg-background">
        <Loader2 className="size-8 animate-spin text-sidebar-primary" />
        <p className="text-sm text-muted-foreground font-medium">Carregando entrevista da IA...</p>
      </div>
    );
  }

  if (entrevistaConcluida) {
    return (
      <div className="flex h-full flex-col items-center justify-center p-6 bg-background">
        <Card className="max-w-md w-full rounded-3xl border-border/60 shadow-xl text-center p-6 bg-card">
          <CardHeader className="flex flex-col items-center gap-2">
            <div className="flex size-14 items-center justify-center rounded-full bg-green-500/10 text-green-500 mb-2">
              <CheckCircle2 className="size-8" />
            </div>
            <CardTitle className="text-2xl font-semibold tracking-tight">
              Entrevista Concluída!
            </CardTitle>
            <CardDescription className="text-sm text-muted-foreground">
              Seu perfil comportamental foi processado e salvo com sucesso.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-6 pt-4">
            <p className="text-sm text-muted-foreground">
              Obrigado por responder nossas perguntas técnico-comportamentais. As notas e feedbacks já estão disponíveis na dashboard do recrutador para análise.
            </p>
            <div className="flex flex-col gap-3">
              <Link href="/">
                <Button className="w-full rounded-xl">Voltar para Vagas</Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col bg-background/50">
      {/* Hidden audio element for browser playbacks */}
      <audio
        ref={audioRef}
        className="hidden"
        onEnded={() => setPlayingAudioUrl(null)}
      />

      {/* Header bar */}
      <header className="flex h-16 shrink-0 items-center justify-between border-b border-border/40 bg-card px-6">
        <div className="flex items-center gap-3">
          <Link href="/">
            <Button variant="ghost" size="icon" className="rounded-full">
              <ChevronLeft className="size-5" />
            </Button>
          </Link>
          <div>
            <h2 className="text-sm font-semibold text-foreground">Entrevista Virtual</h2>
            <p className="text-xs text-muted-foreground">VoiceMatchAi • Análise de Perfil</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="flex size-2 rounded-full bg-emerald-500"></span>
          <span className="text-xs font-semibold text-emerald-500 uppercase tracking-wider">
            Online
          </span>
        </div>
      </header>

      {/* Messages area */}
      <ScrollArea className="flex-1 px-6 py-6">
        <div className="mx-auto flex max-w-3xl flex-col gap-6">
          
          {/* Welcome Card */}
          <div className="rounded-2xl border border-border/40 bg-card/60 p-4 text-center text-xs text-muted-foreground max-w-lg mx-auto shadow-sm">
            Esta é uma entrevista guiada por inteligência artificial. Fale claramente e de forma sincera. Suas respostas de voz serão transcritas e avaliadas para traçar seu perfil de habilidades e atitudes.
          </div>

          {interacoes.map((item) => {
            const isPlaying = playingAudioUrl === item.pergunta_audio_url;

            return (
              <div key={item.id} className="flex flex-col gap-4">
                {/* AI / Interviewer Question */}
                <div className="flex items-start gap-3 max-w-[80%]">
                  <div className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground shadow-md">
                    <Sparkles className="size-4" />
                  </div>
                  <div className="flex flex-col gap-1.5">
                    <div className="rounded-2xl rounded-tl-none bg-card px-4 py-3 border border-border/40 text-sm text-foreground shadow-sm relative group">
                      <p className="leading-relaxed">{item.pergunta_texto}</p>
                      {item.pergunta_audio_url && (
                        <button
                          onClick={() => tocarAudio(item.pergunta_audio_url!)}
                          className={`absolute -right-10 top-1/2 -translate-y-1/2 flex size-7 items-center justify-center rounded-full border transition-all ${
                            isPlaying
                              ? "bg-sidebar-primary border-sidebar-primary text-sidebar-primary-foreground animate-pulse"
                              : "bg-background border-border hover:bg-muted text-muted-foreground"
                          }`}
                        >
                          {isPlaying ? (
                            <Volume2 className="size-3.5" />
                          ) : (
                            <Play className="size-3.5 fill-current ml-0.5" />
                          )}
                        </button>
                      )}
                    </div>
                    <span className="text-[10px] text-muted-foreground pl-1">Entrevistador</span>
                  </div>
                </div>

                {/* Candidate Response */}
                {item.resposta_texto ? (
                  <div className="flex items-start gap-3 max-w-[80%] self-end flex-row-reverse">
                    <div className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-muted text-muted-foreground">
                      <Mic className="size-4" />
                    </div>
                    <div className="flex flex-col gap-1.5 items-end">
                      <div className="rounded-2xl rounded-tr-none bg-sidebar-primary text-sidebar-primary-foreground px-4 py-3 text-sm shadow-sm leading-relaxed">
                        {item.resposta_texto}
                      </div>
                      <span className="text-[10px] text-muted-foreground pr-1">Você</span>
                    </div>
                  </div>
                ) : (
                  // Show thinking bubble if processing this interaction's response
                  processandoResposta && currentInteracao?.id === item.id && (
                    <div className="flex items-start gap-3 max-w-[80%] self-end flex-row-reverse animate-pulse">
                      <div className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-muted text-muted-foreground">
                        <Loader2 className="size-4 animate-spin" />
                      </div>
                      <div className="rounded-2xl bg-muted/40 px-4 py-3 text-sm text-muted-foreground italic shadow-inner">
                        Transcrevendo áudio e formulando avaliação...
                      </div>
                    </div>
                  )
                )}
              </div>
            );
          })}
          
          <div ref={scrollAreaEndRef} />
        </div>
      </ScrollArea>

      {/* Audio input bar */}
      <footer className="shrink-0 border-t border-border/40 bg-card p-6">
        <div className="mx-auto max-w-3xl flex flex-col items-center justify-center gap-4">
          <AudioRecorder
            disabled={processandoResposta}
            onRecordingComplete={enviarResposta}
          />
          <p className="text-[10px] text-muted-foreground text-center">
            Pressione o botão para começar a falar. Responda com calma no seu próprio ritmo.
          </p>
        </div>
      </footer>
    </div>
  );
}
