import type { Candidato } from "@/types";

export interface ResumoVagaBadge {
  label: string;
  variant: "default" | "secondary" | "outline";
}

// Deriva o badge de status da vaga a partir dos status reais dos candidatos —
// nunca um valor fixo.
export function getResumoVagaBadge(candidatos: Candidato[]): ResumoVagaBadge {
  if (candidatos.length === 0) {
    return { label: "Sem candidatos", variant: "outline" };
  }

  const emEntrevista = candidatos.filter(
    (candidato) => candidato.status === "em_entrevista"
  ).length;
  if (emEntrevista > 0) {
    return {
      label: `${emEntrevista} em entrevista`,
      variant: "default",
    };
  }

  const aguardando = candidatos.filter(
    (candidato) => candidato.status === "aguardando"
  ).length;
  if (aguardando > 0) {
    return {
      label: `${aguardando} aguardando triagem`,
      variant: "secondary",
    };
  }

  return { label: "Entrevistas concluídas", variant: "outline" };
}
