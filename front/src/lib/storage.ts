// Camada de dados isolada. Hoje persiste em localStorage; no futuro, troque o
// corpo destas funções por chamadas a uma API/backend (Supabase, Firebase, REST)
// mantendo as mesmas assinaturas — nenhuma tela deve importar localStorage direto.

import type { Candidato, MensagemChat, Vaga } from "@/types";

const KEYS = {
  vagas: "voicematch:vagas",
  candidatos: "voicematch:candidatos",
  mensagens: "voicematch:mensagens",
} as const;

function isBrowser() {
  return typeof window !== "undefined";
}

function readList<T>(key: string): T[] {
  if (!isBrowser()) return [];
  const raw = window.localStorage.getItem(key);
  if (!raw) return [];
  try {
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? (parsed as T[]) : [];
  } catch {
    return [];
  }
}

function writeList<T>(key: string, list: T[]) {
  if (!isBrowser()) return;
  window.localStorage.setItem(key, JSON.stringify(list));
}

// Vagas

export function getVagas(): Vaga[] {
  return readList<Vaga>(KEYS.vagas).sort(
    (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
  );
}

export function getVagaById(id: string): Vaga | null {
  return getVagas().find((vaga) => vaga.id === id) ?? null;
}

export function saveVaga(vaga: Vaga): Vaga {
  const vagas = readList<Vaga>(KEYS.vagas);
  vagas.push(vaga);
  writeList(KEYS.vagas, vagas);
  return vaga;
}

// Candidatos

export function getCandidatos(): Candidato[] {
  return readList<Candidato>(KEYS.candidatos).sort(
    (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
  );
}

export function getCandidatosByVaga(vagaId: string): Candidato[] {
  return getCandidatos().filter((candidato) => candidato.vagaId === vagaId);
}

export function getCandidatoById(id: string): Candidato | null {
  return getCandidatos().find((candidato) => candidato.id === id) ?? null;
}

export function saveCandidato(candidato: Candidato): Candidato {
  const candidatos = readList<Candidato>(KEYS.candidatos);
  candidatos.push(candidato);
  writeList(KEYS.candidatos, candidatos);
  return candidato;
}

export function updateCandidato(
  id: string,
  changes: Partial<Omit<Candidato, "id">>
): Candidato | null {
  const candidatos = readList<Candidato>(KEYS.candidatos);
  const index = candidatos.findIndex((candidato) => candidato.id === id);
  if (index === -1) return null;

  const atualizado = { ...candidatos[index], ...changes };
  candidatos[index] = atualizado;
  writeList(KEYS.candidatos, candidatos);
  return atualizado;
}

// Mensagens do chat de entrevista

export function getMensagensByCandidato(candidatoId: string): MensagemChat[] {
  return readList<MensagemChat>(KEYS.mensagens)
    .filter((mensagem) => mensagem.candidatoId === candidatoId)
    .sort(
      (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    );
}

export function saveMensagem(mensagem: MensagemChat): MensagemChat {
  const mensagens = readList<MensagemChat>(KEYS.mensagens);
  mensagens.push(mensagem);
  writeList(KEYS.mensagens, mensagens);
  return mensagem;
}
