import type { Metadata } from "next";
import { Fraunces, Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";
import { cn } from "@/lib/utils";
import { ThemeProvider } from "@/context/theme-provider";
import { TooltipProvider } from "@/_components/ui/tooltip";
import { Toaster } from "@/_components/ui/sonner";
import { Sidebar } from "@/_components/layout/sidebar";

const bodyFont = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--font-sans",
});

const headingFont = Fraunces({
  subsets: ["latin"],
  variable: "--font-heading",
  axes: ["opsz", "SOFT", "WONK"],
});

export const metadata: Metadata = {
  title: "VoiceMatchAi",
  description: "Entrevistas por chat com match de perfil comportamental",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="pt-BR"
      className={cn("h-full", "antialiased", bodyFont.variable, headingFont.variable)}
      suppressHydrationWarning
    >
      <body className="h-full font-sans">
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <TooltipProvider>
            <div className="flex h-svh">
              <Sidebar />
              <main className="flex-1 overflow-hidden">{children}</main>
            </div>
            <Toaster />
          </TooltipProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
