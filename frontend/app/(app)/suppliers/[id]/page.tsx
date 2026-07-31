import { SupplierDetailClient } from "@/components/supplier-detail-client";

export default async function SupplierDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <SupplierDetailClient supplierId={id} />;
}
