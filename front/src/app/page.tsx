"use client";

import { Briefcase, Plus } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

import {
  Avatar,
  AvatarFallback,
  AvatarGroup,
  AvatarGroupCount,
  AvatarImage,
} from "@/_components/ui/avatar";
import { Badge } from "@/_components/ui/badge";
import { Button } from "@/_components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/_components/ui/card";
import { ScrollArea } from "@/_components/ui/scroll-area";
import { NovaVagaDialog } from "@/_components/vagas/nova-vaga-dialog";
import { getCandidatosByVaga, getVagas } from "@/lib/storage";
import { getResumoVagaBadge } from "@/lib/vaga-status";
import type { Candidato, Vaga } from "@/types";

function carregarVagasComCandidatos(): {
  vagas: Vaga[];
  candidatosPorVaga: Record<string, Candidato[]>;
} {
  const vagasSalvas = getVagas();
  return {
    vagas: vagasSalvas,
    candidatosPorVaga: Object.fromEntries(
      vagasSalvas.map((vaga) => [vaga.id, getCandidatosByVaga(vaga.id)])
    ),
  };
}

export default function DashboardPage() {
  const [dados, setDados] = useState<{
    vagas: Vaga[];
    candidatosPorVaga: Record<string, Candidato[]>;
  }>({ vagas: [], candidatosPorVaga: {} });
  const [novaVagaOpen, setNovaVagaOpen] = useState(false);

  useEffect(() => {
    // localStorage não existe no SSR; a leitura real só é possível depois do
    // mount no cliente, por isso o estado inicial é preenchido aqui.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setDados(carregarVagasComCandidatos());
  }, []);

  const { vagas, candidatosPorVaga } = dados;

  return (
    <>
      <ScrollArea className="h-full">
        <div className="mx-auto flex max-w-5xl flex-col gap-8 px-6 py-10">
          <header className="flex items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl font-semibold tracking-tight">
                Vagas
              </h1>
              <p className="text-sm text-muted-foreground">
                Acompanhe as vagas abertas e o andamento das entrevistas.
              </p>
            </div>

            <Button onClick={() => setNovaVagaOpen(true)}>
              <Plus data-icon="inline-start" />
              Nova vaga
            </Button>
          </header>

          {vagas.length === 0 ? (
            <div className="flex flex-col items-center gap-4 rounded-3xl border border-dashed border-border py-20 text-center">
              <span className="flex size-12 items-center justify-center rounded-full bg-muted text-muted-foreground">
                <Briefcase className="size-5" />
              </span>
              <div className="flex flex-col gap-1">
                <p className="font-heading text-lg font-medium">
                  Nenhuma vaga criada ainda
                </p>
                <p className="max-w-sm text-sm text-muted-foreground">
                  Crie sua primeira vaga para começar a receber e avaliar
                  candidatos.
                </p>
              </div>
              <Button onClick={() => setNovaVagaOpen(true)}>
                <Plus data-icon="inline-start" />
                Criar primeira vaga
              </Button>
            </div>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {vagas.map((vaga) => {
                const candidatos = candidatosPorVaga[vaga.id] ?? [];
                const badge = getResumoVagaBadge(candidatos);

                return (
                  <Link
                    key={vaga.id}
                    href={`/vagas/${vaga.id}`}
                    className="block rounded-[min(var(--radius-4xl),24px)] outline-none transition-shadow focus-visible:ring-3 focus-visible:ring-ring/30"
                  >
                    <Card className="h-full transition-shadow hover:shadow-md">
                      <CardHeader>
                        <CardTitle>{vaga.titulo}</CardTitle>
                        <CardDescription>
                          {vaga.area} • {vaga.funcao}
                        </CardDescription>
                      </CardHeader>

                      <CardContent className="flex flex-col gap-4">
                        <Badge variant={badge.variant} className="w-fit">
                          {badge.label}
                        </Badge>

                        <div className="flex items-center justify-between">
                          <span className="text-sm text-muted-foreground">
                            {candidatos.length === 0
                              ? "Nenhum candidato"
                              : candidatos.length === 1
                                ? "1 candidato"
                                : `${candidatos.length} candidatos`}
                          </span>

                          {candidatos.length > 0 && (
                            <AvatarGroup>
                              {candidatos.slice(0, 3).map((candidato) => (
                                <Avatar key={candidato.id} size="sm">
                                  {candidato.avatarUrl && (
                                    <AvatarImage
                                      src={candidato.avatarUrl}
                                      alt={candidato.nome}
                                    />
                                  )}
                                  <AvatarFallback>
                                    {candidato.nome.charAt(0).toUpperCase()}
                                  </AvatarFallback>
                                </Avatar>
                              ))}
                              {candidatos.length > 3 && (
                                <AvatarGroupCount>
                                  +{candidatos.length - 3}
                                </AvatarGroupCount>
                              )}
                            </AvatarGroup>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  </Link>
                );
              })}
            </div>
          )}
        </div>
      </ScrollArea>

      <NovaVagaDialog
        open={novaVagaOpen}
        onOpenChange={setNovaVagaOpen}
        onVagaCriada={() => setDados(carregarVagasComCandidatos())}
      />
    </>
  );
}
