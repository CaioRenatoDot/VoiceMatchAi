"use client";

import { Briefcase, LayoutDashboard, Mic } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { ThemeToggle } from "@/_components/layout/theme-toggle";
import { Separator } from "@/_components/ui/separator";
import { cn } from "@/lib/utils";

const NAV = [
  { href: "/", label: "Dashboard", icone: LayoutDashboard },
  { href: "/vagas", label: "Vagas", icone: Briefcase },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex h-svh w-60 shrink-0 flex-col justify-between border-r border-sidebar-border bg-sidebar px-4 py-5 text-sidebar-foreground">
      <div className="flex flex-col gap-6">
        <Link href="/" className="flex items-center gap-2 px-1">
          <span className="flex size-8 items-center justify-center rounded-xl bg-sidebar-primary text-sidebar-primary-foreground">
            <Mic className="size-4" />
          </span>
          <span className="font-heading text-lg font-semibold tracking-tight">
            VoiceMatch<span className="text-sidebar-primary">Ai</span>
          </span>
        </Link>

        <nav className="flex flex-col gap-1">
          {NAV.map(({ href, label, icone: Icone }) => {
            // "/" só casa exato; as demais também cobrem as rotas filhas
            // (ex.: /vagas/[id] mantém "Vagas" ativo).
            const ativo =
              href === "/"
                ? pathname === "/"
                : pathname === href || pathname.startsWith(`${href}/`);

            return (
              <Link
                key={href}
                href={href}
                aria-current={ativo ? "page" : undefined}
                className={cn(
                  "flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                  // Ativo: o azul do app diluído. No hover a opacidade cai,
                  // então a cor clareia em vez de escurecer.
                  ativo
                    ? "bg-sidebar-primary/20 text-sidebar-primary hover:bg-sidebar-primary/10 hover:text-sidebar-primary"
                    : "text-sidebar-foreground",
                )}
              >
                <Icone className="size-4" />
                {label}
              </Link>
            );
          })}
        </nav>
      </div>

      <div className="flex items-center justify-between px-1">
        <span className="text-xs text-muted-foreground">Tema</span>
        <ThemeToggle />
      </div>
    </aside>
  );
}
