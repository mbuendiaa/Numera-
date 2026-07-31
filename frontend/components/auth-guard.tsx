"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { ensureActiveCompany } from "@/lib/session";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const check = async () => {
      if (!getAccessToken()) {
        router.replace(`/login?next=${encodeURIComponent(pathname)}`);
        return;
      }
      try {
        const user = await ensureActiveCompany();
        if (!user.company_id) {
          router.replace("/onboarding");
          return;
        }
        setReady(true);
      } catch {
        router.replace("/login");
      }
    };
    void check();
  }, [pathname, router]);

  if (!ready) return <div className="grid min-h-screen place-items-center text-sm text-slate-500">Comprobando cuenta y empresa…</div>;
  return children;
}
