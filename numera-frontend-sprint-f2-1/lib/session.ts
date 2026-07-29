"use client";

import { apiFetch } from "@/lib/api";
import type { User } from "@/lib/types";

export async function routeAfterLogin(): Promise<string> {
  const user = await apiFetch<User>("/auth/me");
  return user.company_id ? "/dashboard" : "/onboarding";
}
