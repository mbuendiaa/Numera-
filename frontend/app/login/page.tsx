"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";
import { apiFetch } from "@/lib/api";
import { saveTokens } from "@/lib/auth";
import { routeAfterLogin } from "@/lib/session";
import type { TokenPair } from "@/lib/types";

export default function LoginPage() {
  const router = useRouter();
  const search = useSearchParams();
  const [email, setEmail] = useState("marta@numera.es");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      const tokens = await apiFetch<TokenPair>("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password })
      });
      saveTokens(tokens.access_token, tokens.refresh_token);
      const destination = search.get("next") || await routeAfterLogin();
      router.replace(destination);
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo iniciar sesión");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="grid min-h-screen place-items-center px-4 py-10">
      <section className="w-full max-w-md rounded-3xl border bg-card p-8 shadow-soft">
        <div className="mb-8">
          <div className="mb-4 inline-flex h-11 w-11 items-center justify-center rounded-2xl bg-primary font-bold text-white">N</div>
          <h1 className="text-3xl font-semibold">Bienvenida a Numera</h1>
          <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">Accede con tu cuenta de Numera.</p>
        </div>

        <form className="space-y-5" onSubmit={submit}>
          <label className="block text-sm font-medium">
            Correo
            <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)}
              className="mt-2 w-full rounded-xl border bg-transparent px-4 py-3 outline-none focus:ring-2 focus:ring-primary" />
          </label>
          <label className="block text-sm font-medium">
            Contraseña
            <input type="password" required value={password} onChange={(e) => setPassword(e.target.value)}
              className="mt-2 w-full rounded-xl border bg-transparent px-4 py-3 outline-none focus:ring-2 focus:ring-primary" />
          </label>

          {error && <div className="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/30 dark:text-red-300">{error}</div>}

          <button type="submit" className="w-full rounded-xl bg-primary px-4 py-3 font-semibold text-white disabled:opacity-60" disabled={loading}>
            {loading ? "Entrando…" : "Entrar"}
          </button>
        </form>

        <div className="mt-7 border-t pt-6 text-center text-sm">
          <span className="text-slate-500">¿Todavía no tienes cuenta? </span>
          <Link href="/register" className="font-semibold text-primary">Crear cuenta</Link>
        </div>
      </section>
    </main>
  );
}
