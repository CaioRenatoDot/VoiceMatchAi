export const TRAITS = [
  "equipe",
  "proatividade",
  "resiliencia",
  "foco_em_resultado",
  "negociacao",
  "relacao_hierarquica",
  "resolucao_de_conflito",
  "inovacao",
  "acao_sob_pressao",
  "assertividade",
  "autenticidade",
  "autonomia",
  "comunicabilidade",
  "cuidado",
  "disciplina",
  "empenho",
  "flexibilidade",
  "seguranca",
  "tranquilidade",
  "vitalidade_corporal",
] as const;

export type Trait = (typeof TRAITS)[number];

export type PerfilComportamental = Record<Trait, number>;

// Perfil neutro (5/10 em todos os traços), usado como valor inicial de
// perfilIdeal enquanto o editor de radar (próxima etapa) ainda não existe.
export function criarPerfilNeutro(): PerfilComportamental {
  return Object.fromEntries(TRAITS.map((trait) => [trait, 5])) as PerfilComportamental;
}

export interface Vaga {
  id: string;
  titulo: string;
  area: string;
  funcao: string;
  descricaoFuncao: string;
  hardSkills: string[];
  softSkills: string[];
  experienciaPrevia: string;
  perfilIdeal: PerfilComportamental;
  createdAt: string;
}

export type StatusCandidato = "aguardando" | "em_entrevista" | "finalizado";

export interface Candidato {
  id: string;
  vagaId: string;
  nome: string;
  avatarUrl: string | null;
  status: StatusCandidato;
  perfilAvaliado: PerfilComportamental | null;
  notaFinal: number | null;
  pontosFortes: string[] | null;
  pontosFracos: string[] | null;
  melhorias: string[] | null;
  createdAt: string;
}

export type AutorMensagem = "ia" | "candidato";
export type TipoMensagem = "texto" | "audio";

export interface MensagemChat {
  id: string;
  candidatoId: string;
  autor: AutorMensagem;
  tipo: TipoMensagem;
  conteudo: string;
  perguntaRelacionada?: Trait[];
  timestamp: string;
  duracaoAudio?: number;
}
