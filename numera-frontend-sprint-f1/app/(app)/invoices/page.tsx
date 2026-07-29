import { UploadCloud } from "lucide-react";
import { PlaceholderPage } from "@/components/placeholder-page";

export default function InvoicesPage() {
  return (
    <PlaceholderPage
      title="Facturas"
      description="Sube, revisa y contabiliza facturas de proveedor."
      action={
        <button className="inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-white">
          <UploadCloud size={18} />
          Subir factura
        </button>
      }
    />
  );
}
