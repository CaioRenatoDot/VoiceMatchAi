"use client";

import { Eye, EyeOff, Mic } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";

import { Button } from "@/_components/ui/button";
import { Card, CardContent } from "@/_components/ui/card";
import { Input } from "@/_components/ui/input";
import { Label } from "@/_components/ui/label";

interface LoginFormValues {
  email: string;
  password: string;
}

export default function LoginPage() {
  const [showPassword, setShowPassword] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormValues>({
    mode: "onBlur",
    defaultValues: { email: "", password: "" },
  });

  async function onSubmit(values: LoginFormValues) {
    // TODO: o backend ainda não expõe login (não há POST /auth/login e o
    // cadastro de recrutador nem recebe senha). Ligar aqui quando existir.
    console.log("login", values);
  }

  return (
    <div className="flex h-full items-center justify-center px-6 py-10">
      <div className="flex w-full max-w-sm flex-col gap-6">
        <div className="flex flex-col items-center gap-3 text-center">
          <span className="flex size-11 items-center justify-center rounded-2xl bg-sidebar-primary text-sidebar-primary-foreground">
            <Mic className="size-5" />
          </span>
          <div className="flex flex-col gap-1">
            <h1 className="font-heading text-2xl font-semibold tracking-tight">
              Entrar na VoiceMatch<span className="text-sidebar-primary">Ai</span>
            </h1>
            <p className="text-sm text-muted-foreground">
              Acesse com seu e-mail e senha de recrutador.
            </p>
          </div>
        </div>

        <Card>
          <CardContent>
            <form
              onSubmit={handleSubmit(onSubmit)}
              noValidate
              className="flex flex-col gap-5"
            >
              <div className="flex flex-col gap-2">
                <Label htmlFor="email">E-mail</Label>
                <Input
                  id="email"
                  type="email"
                  autoComplete="email"
                  placeholder="voce@empresa.com"
                  aria-invalid={errors.email ? true : undefined}
                  aria-describedby={errors.email ? "email-error" : undefined}
                  {...register("email", {
                    required: "Informe seu e-mail.",
                    pattern: {
                      value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                      message: "E-mail inválido.",
                    },
                  })}
                />
                {errors.email && (
                  <p
                    id="email-error"
                    role="alert"
                    className="text-sm text-destructive"
                  >
                    {errors.email.message}
                  </p>
                )}
              </div>

              <div className="flex flex-col gap-2">
                <Label htmlFor="password">Senha</Label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    autoComplete="current-password"
                    placeholder="••••••••"
                    className="pr-9"
                    aria-invalid={errors.password ? true : undefined}
                    aria-describedby={
                      errors.password ? "password-error" : undefined
                    }
                    {...register("password", {
                      required: "Informe sua senha.",
                      minLength: {
                        value: 8,
                        message: "A senha deve ter ao menos 8 caracteres.",
                      },
                    })}
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon-xs"
                    onClick={() => setShowPassword((current) => !current)}
                    aria-label={showPassword ? "Ocultar senha" : "Mostrar senha"}
                    className="absolute inset-y-0 right-1 my-auto text-muted-foreground"
                  >
                    {showPassword ? <EyeOff /> : <Eye />}
                  </Button>
                </div>
                {errors.password && (
                  <p
                    id="password-error"
                    role="alert"
                    className="text-sm text-destructive"
                  >
                    {errors.password.message}
                  </p>
                )}
              </div>

              <Button type="submit" size="lg" disabled={isSubmitting}>
                {isSubmitting ? "Entrando..." : "Entrar"}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
