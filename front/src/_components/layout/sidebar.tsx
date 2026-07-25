import { Mic, Briefcase } from "lucide-react";
import Link from "next/link";

import { ThemeToggle } from "@/_components/layout/theme-toggle";
import { Separator } from "@/_components/ui/separator";

export function Sidebar() {
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

        <Separator />

        <nav className="flex flex-col gap-1">
          <Link
            href="/"
            className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
          >
            <Briefcase className="size-4" />
            Vagas
          </Link>
        </nav>
      </div>

      <div className="flex items-center justify-between px-1">
        <span className="text-xs text-muted-foreground">Tema</span>
        <ThemeToggle />
      </div>
    </aside>
  );
}
