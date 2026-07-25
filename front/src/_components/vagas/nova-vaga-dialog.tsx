"use client";

import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/_components/ui/button";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/_components/ui/dialog";
import { Input } from "@/_components/ui/input";
import { Label } from "@/_components/ui/label";
import { ScrollArea } from "@/_components/ui/scroll-area";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/_components/ui/select";
import { TagInput } from "@/_components/ui/tag-input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/_components/ui/tabs";
import { Textarea } from "@/_components/ui/textarea";
import { saveVaga } from "@/lib/storage";
import { criarPerfilNeutro, type Vaga } from "@/types";

const AREAS = [
  "Comercial & Vendas",
  "Marketing",
  "Produto",
  "Tecnologia",
  "Operações",
  "Financeiro",
  "Recursos Humanos",
  "Atendimento ao Cliente",
  "Outra",
];

const NIVEIS_EXPERIENCIA = [
  "Sem experiência prévia",
  "Júnior (1-2 anos)",
  "Pleno (3-5 anos)",
  "Sênior (5+ anos)",
];

const CAMPOS_INICIAIS = {
  titulo: "",
  area: "",
  funcao: "",
  descricaoFuncao: "",
  hardSkills: [] as string[],
  softSkills: [] as string[],
  experienciaPrevia: "",
};

interface NovaVagaDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onVagaCriada: () => void;
}

export function NovaVagaDialog({
  open,
  onOpenChange,
  onVagaCriada,
}: NovaVagaDialogProps) {
  const [campos, setCampos] = useState(CAMPOS_INICIAIS);

  function handleOpenChange(nextOpen: boolean) {
    onOpenChange(nextOpen);
    if (!nextOpen) {
      setCampos(CAMPOS_INICIAIS);
    }
  }

  const valido =
    campos.titulo.trim() !== "" &&
    campos.area !== "" &&
    campos.funcao.trim() !== "";

  function handleSalvar() {
    if (!valido) return;

    const vaga: Vaga = {
      id: crypto.randomUUID(),
      titulo: campos.titulo.trim(),
      area: campos.area,
      funcao: campos.funcao.trim(),
      descricaoFuncao: campos.descricaoFuncao.trim(),
      hardSkills: campos.hardSkills,
      softSkills: campos.softSkills,
      experienciaPrevia: campos.experienciaPrevia,
      perfilIdeal: criarPerfilNeutro(),
      createdAt: new Date().toISOString(),
    };

    saveVaga(vaga);
    toast.success("Vaga criada com sucesso", { description: vaga.titulo });
    handleOpenChange(false);
    onVagaCriada();
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="max-w-4xl">
        <DialogHeader>
          <DialogTitle>Nova vaga</DialogTitle>
          <DialogDescription>
            Preencha os requisitos da vaga. O perfil comportamental ideal
            (radar de 20 traços) é configurado na próxima etapa.
          </DialogDescription>
        </DialogHeader>

        <Tabs defaultValue="requisitos">
          <TabsList>
            <TabsTrigger value="requisitos">Requisitos</TabsTrigger>
            <TabsTrigger value="perfil">Perfil ideal</TabsTrigger>
          </TabsList>

          <TabsContent value="requisitos">
            <ScrollArea className="h-[55vh] pr-4">
              <div className="flex flex-col gap-5 py-1 pr-1">
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="flex flex-col gap-2">
                    <Label htmlFor="titulo">Título da vaga *</Label>
                    <Input
                      id="titulo"
                      placeholder="Ex: Analista de Vendas Pleno"
                      value={campos.titulo}
                      onChange={(event) =>
                        setCampos((prev) => ({
                          ...prev,
                          titulo: event.target.value,
                        }))
                      }
                    />
                  </div>

                  <div className="flex flex-col gap-2">
                    <Label htmlFor="area">Área *</Label>
                    <Select
                      value={campos.area || undefined}
                      onValueChange={(value) =>
                        setCampos((prev) => ({ ...prev, area: String(value) }))
                      }
                    >
                      <SelectTrigger id="area" className="w-full">
                        <SelectValue placeholder="Selecione a área" />
                      </SelectTrigger>
                      <SelectContent>
                        {AREAS.map((area) => (
                          <SelectItem key={area} value={area}>
                            {area}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="flex flex-col gap-2">
                  <Label htmlFor="funcao">Função *</Label>
                  <Input
                    id="funcao"
                    placeholder="Ex: Responsável por prospecção e fechamento de contas PME"
                    value={campos.funcao}
                    onChange={(event) =>
                      setCampos((prev) => ({
                        ...prev,
                        funcao: event.target.value,
                      }))
                    }
                  />
                </div>

                <div className="flex flex-col gap-2">
                  <Label htmlFor="descricaoFuncao">Descrição da função</Label>
                  <Textarea
                    id="descricaoFuncao"
                    placeholder="Descreva as responsabilidades e o contexto da vaga"
                    value={campos.descricaoFuncao}
                    onChange={(event) =>
                      setCampos((prev) => ({
                        ...prev,
                        descricaoFuncao: event.target.value,
                      }))
                    }
                  />
                </div>

                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="flex flex-col gap-2">
                    <Label htmlFor="hardSkills">Hard skills</Label>
                    <TagInput
                      id="hardSkills"
                      placeholder="Digite e pressione Enter"
                      value={campos.hardSkills}
                      onChange={(tags) =>
                        setCampos((prev) => ({ ...prev, hardSkills: tags }))
                      }
                    />
                  </div>

                  <div className="flex flex-col gap-2">
                    <Label htmlFor="softSkills">Soft skills</Label>
                    <TagInput
                      id="softSkills"
                      placeholder="Digite e pressione Enter"
                      value={campos.softSkills}
                      onChange={(tags) =>
                        setCampos((prev) => ({ ...prev, softSkills: tags }))
                      }
                    />
                  </div>
                </div>

                <div className="flex flex-col gap-2">
                  <Label htmlFor="experiencia">Experiência prévia</Label>
                  <Select
                    value={campos.experienciaPrevia || undefined}
                    onValueChange={(value) =>
                      setCampos((prev) => ({
                        ...prev,
                        experienciaPrevia: String(value),
                      }))
                    }
                  >
                    <SelectTrigger id="experiencia" className="w-full sm:w-72">
                      <SelectValue placeholder="Selecione o nível esperado" />
                    </SelectTrigger>
                    <SelectContent>
                      {NIVEIS_EXPERIENCIA.map((nivel) => (
                        <SelectItem key={nivel} value={nivel}>
                          {nivel}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </ScrollArea>
          </TabsContent>

          <TabsContent value="perfil">
            <div className="flex h-[55vh] flex-col items-center justify-center gap-2 text-center text-sm text-muted-foreground">
              <p className="font-heading text-base font-medium text-foreground">
                Perfil comportamental ideal
              </p>
              <p className="max-w-sm">
                O radar arrastável com os 20 traços comportamentais chega na
                próxima parte. Por enquanto a vaga é criada com um perfil
                neutro (5/10 em todos os traços).
              </p>
            </div>
          </TabsContent>
        </Tabs>

        <DialogFooter>
          <DialogClose render={<Button variant="outline" />}>
            Cancelar
          </DialogClose>
          <Button onClick={handleSalvar} disabled={!valido}>
            Criar vaga
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
