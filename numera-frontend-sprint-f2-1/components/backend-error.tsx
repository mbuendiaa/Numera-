import { ServerCrash } from "lucide-react";

export function BackendError({ message, retry }: { message: string; retry?: () => void }) {
  return (
    <div className="rounded-3xl border border-dashed bg-card p-10 text-center shadow-soft">
      <ServerCrash className="mx-auto text-slate-400" size={38} />
      <h2 className="mt-4 text-lg font-semibold">No se pudieron cargar los datos</h2>
      <p className="mx-auto mt-2 max-w-xl text-sm text-slate-500 dark:text-slate-400">{message}</p>
      {retry && <button onClick={retry} className="mt-5 rounded-xl bg-primary px-4 py-2 text-sm font-semibold text-white">Reintentar</button>}
    </div>
  );
}
