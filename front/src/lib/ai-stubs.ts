// Funções que hoje simulam comportamento de IA/hardware real. Cada uma está
// marcada com STUB: a assinatura é definitiva, mas a implementação atual é
// local e determinística/simulada. Quando houver backend + IA real, troque só
// o corpo destas funções — nenhuma tela deve mudar.

import type { MensagemChat, PerfilComportamental, Trait, Vaga } from "@/types";

export interface PerguntaGerada {
  texto: string;
  traits: Trait[];
}

// STUB: substituir por chamada real à API depois (geração de perguntas via LLM)
export function generateInterviewQuestions(_vaga: Vaga): PerguntaGerada[] {
  throw new Error("generateInterviewQuestions ainda não implementado");
}

// STUB: substituir por chamada real à API depois (transcrição + avaliação da resposta em áudio)
export function simulateCandidateAnswer(
  _pergunta: PerguntaGerada,
  _vaga: Vaga
): Pick<MensagemChat, "conteudo" | "duracaoAudio"> {
  throw new Error("simulateCandidateAnswer ainda não implementado");
}

export interface ResultadoAvaliacao {
  notaFinal: number;
  pontosFortes: string[];
  pontosFracos: string[];
  melhorias: string[];
}

// STUB: hoje é cálculo local determinístico (comparação de perfis); no futuro
// pode incorporar avaliação de IA sobre as respostas em texto/áudio
export function calculateScore(
  _perfilIdeal: PerfilComportamental,
  _perfilAvaliado: PerfilComportamental
): ResultadoAvaliacao {
  throw new Error("calculateScore ainda não implementado");
}
