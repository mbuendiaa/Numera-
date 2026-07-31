"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { apiFetch } from "@/lib/api";
import { saveTokens } from "@/lib/auth";
import type { TokenPair, User } from "@/lib/types";

export default function RegisterPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      await apiFetch<User>("/auth/register", {
        method: "POST",
        body: JSON.stringify({ name, email, password })
      });

      const tokens = await apiFetch<TokenPair>("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password })
      });
      saveTokens(tokens.access_token, tokens.refresh_token);

      sessionStorage.setItem("numera_pending_company_name", companyName.trim());
      router.replace("/onboarding");
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo crear la cuenta");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="grid min-h-screen place-items-center px-4 py-10">
      <section className="w-full max-w-lg rounded-3xl border bg-card p-8 shadow-soft">
        <div className="mb-8">
          <div className="mb-4 inline-flex h-11 w-11 items-center justify-center rounded-2xl bg-primary font-bold text-white">N</div>
          <h1 className="text-3xl font-semibold">Crea tu cuenta</h1>
          <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">Tu primera empresa quedará vinculada a ti como administradora principal.</p>
        </div>

        <form className="grid gap-5" onSubmit={submit}>
          <label className="block text-sm font-medium">
            Nombre
            <input required value={name} onChange={(e) => setName(e.target.value)}
              className="mt-2 w-full rounded-xl border bg-transparent px-4 py-3 outline-none focus:ring-2 focus:ring-primary" placeholder="Marta" />
          </label>
          <label className="block text-sm font-medium">
            Correo
            <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)}
              className="mt-2 w-full rounded-xl border bg-transparent px-4 py-3 outline-none focus:ring-2 focus:ring-primary" placeholder="marta@empresa.es" />
          </label>
          <label className="block text-sm font-medium">
            Contraseña
            <input type="password" minLength={8} required value={password} onChange={(e) => setPassword(e.target.value)}
              className="mt-2 w-full rounded-xl border bg-transparent px-4 py-3 outline-none focus:ring-2 focus:ring-primary" placeholder="Mínimo 8 caracteres" />
          </label>
          <label className="block text-sm font-medium">
            Nombre de la empresa
            <input required value={companyName} onChange={(e) => setCompanyName(e.target.value)}
              className="mt-2 w-full rounded-xl border bg-transparent px-4 py-3 outline-none focus:ring-2 focus:ring-primary" placeholder="Mi empresa S.L." />
          </label>

          {error && <div className="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/30 dark:text-red-300">{error}</div>}

          <button type="submit" className="rounded-xl bg-primary px-4 py-3 font-semibold text-white disabled:opacity-60" disabled={loading}>
            {loading ? "Creando cuenta…" : "Crear cuenta y empresa"}
          </button>
        </form>

        <div className="mt-7 border-t pt-6 text-center text-sm">
          <span className="text-slate-500">¿Ya tienes cuenta? </span>
          <Link href="/login" className="font-semibold text-primary">Iniciar sesión</Link>
        </div>
      </section>
    </main>
  );
}
