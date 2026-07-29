"use client";

import { useRef, useState } from "react";
import { FileCheck2, LoaderCircle, UploadCloud, X } from "lucide-react";
import { apiFetch } from "@/lib/api";
import type { UploadResponse } from "@/lib/types";

const steps = ["Subiendo PDF", "Ejecutando OCR", "Extrayendo campos", "Creando catálogo", "Generando asiento"];

export function InvoiceUpload({ onSuccess }: { onSuccess: (result: UploadResponse) => void }) {
  const input = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [dragging, setDragging] = useState(false);
  const [running, setRunning] = useState(false);
  const [step, setStep] = useState(0);
  const [error, setError] = useState("");

  async function upload() {
    if (!file) return;
    setRunning(true);
    setError("");
    setStep(0);

    const timer = window.setInterval(() => setStep((value) => Math.min(value + 1, steps.length - 1)), 900);
    try {
      const body = new FormData();
      body.append("file", file);
      const result = await apiFetch<UploadResponse>("/documents/upload", { method: "POST", body });
      onSuccess(result);
      setFile(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo procesar el PDF");
    } finally {
      window.clearInterval(timer);
      setRunning(false);
    }
  }

  function choose(next: File | undefined) {
    if (!next) return;
    if (next.type !== "application/pdf") {
      setError("Selecciona un archivo PDF.");
      return;
    }
    setError("");
    setFile(next);
  }

  return (
    <section className="rounded-3xl border bg-card p-6 shadow-soft">
      <div className="mb-5">
        <h2 className="text-lg font-semibold">Subir factura</h2>
        <p className="text-sm text-slate-500 dark:text-slate-400">El backend hará OCR, extracción, catálogo y propuesta contable.</p>
      </div>

      <input ref={input} type="file" accept="application/pdf" className="hidden" onChange={(e) => choose(e.target.files?.[0])} />

      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => { e.preventDefault(); setDragging(false); choose(e.dataTransfer.files[0]); }}
        onClick={() => !running && input.current?.click()}
        className={`cursor-pointer rounded-2xl border-2 border-dashed p-9 text-center transition ${dragging ? "border-primary bg-primary/5" : "hover:bg-muted/60"}`}
      >
        <UploadCloud className="mx-auto text-slate-400" size={36} />
        <p className="mt-4 font-semibold">{file ? file.name : "Arrastra aquí una factura PDF"}</p>
        <p className="mt-1 text-sm text-slate-500">{file ? `${(file.size / 1024).toFixed(0)} KB` : "o pulsa para seleccionar el archivo"}</p>
      </div>

      {running && (
        <div className="mt-5 rounded-2xl bg-muted p-4">
          <div className="flex items-center gap-3">
            <LoaderCircle className="animate-spin" size={19} />
            <div>
              <p className="text-sm font-medium">{steps[step]}…</p>
              <p className="text-xs text-slate-500">No cierres esta pantalla.</p>
            </div>
          </div>
          <div className="mt-3 h-2 overflow-hidden rounded-full bg-background">
            <div className="h-full bg-primary transition-all" style={{ width: `${((step + 1) / steps.length) * 100}%` }} />
          </div>
        </div>
      )}

      {error && <div className="mt-4 rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/30 dark:text-red-300">{error}</div>}

      <div className="mt-5 flex justify-end gap-3">
        {file && !running && <button onClick={() => setFile(null)} className="inline-flex items-center gap-2 rounded-xl border px-4 py-2.5 text-sm"><X size={17} />Quitar</button>}
        <button disabled={!file || running} onClick={upload} className="inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-50">
          <FileCheck2 size={18} /> Procesar factura
        </button>
      </div>
    </section>
  );
}
