"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

export default function LoginPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setTimeout(() => router.push("/dashboard"), 500);
  }

  return (
    <main className="grid min-h-screen place-items-center px-4">
      <section className="w-full max-w-md rounded-3xl border bg-card p-8 shadow-soft">
        <div className="mb-8">
          <div className="mb-4 inline-flex h-11 w-11 items-center justify-center rounded-2xl bg-primary font-bold text-white">N</div>
          <h1 className="text-3xl font-semibold">Bienvenida a Numera</h1>
          <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">Accede a la gestión inteligente de tu empresa.</p>
        </div>

        <form className="space-y-5" onSubmit={submit}>
          <label className="block text-sm font-medium">
            Correo
            <input
              type="email"
              required
              defaultValue="marta@numera.es"
              className="mt-2 w-full rounded-xl border bg-transparent px-4 py-3 outline-none focus:ring-2 focus:ring-primary"
            />
          </label>
          <label className="block text-sm font-medium">
            Contraseña
            <input
              type="password"
              required
              defaultValue="numera"
              className="mt-2 w-full rounded-xl border bg-transparent px-4 py-3 outline-none focus:ring-2 focus:ring-primary"
            />
          </label>
          <button
            type="submit"
            className="w-full rounded-xl bg-primary px-4 py-3 font-semibold text-white transition hover:opacity-90 disabled:opacity-60"
            disabled={loading}
          >
            {loading ? "Entrando..." : "Entrar"}
          </button>
        </form>

        <p className="mt-6 text-center text-xs text-slate-400">Demo local: no valida credenciales.</p>
      </section>
    </main>
  );
}
