import Link from "next/link";

import { Button } from "@/_components/ui/button";

export default async function VagaDetalhePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  return (
    <div className="mx-auto flex max-w-5xl flex-col gap-4 px-6 py-10">
      <Button variant="ghost" size="sm" render={<Link href="/vagas" />}>
        Voltar para vagas
      </Button>

      <div className="flex flex-col gap-1">
        <h1 className="text-2xl font-semibold tracking-tight">
          Detalhe da vaga
        </h1>
        <p className="text-sm text-muted-foreground">
          Vaga #{id} — requisitos e lista de candidatos chegam na Etapa 3.
        </p>
      </div>
    </div>
  );
}
