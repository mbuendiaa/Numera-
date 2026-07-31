"use client";

import { apiFetch } from "@/lib/api";
import type { Company, User } from "@/lib/types";

type CompanyWithRole = Company & {
  selected?: boolean;
  is_active?: boolean;
  role?: string;
};

/**
 * Makes sure the authenticated user has an active company.
 *
 * This also repairs accounts created with older versions of Numera where the
 * membership existed but the selected company was not persisted on the user.
 */
export async function ensureActiveCompany(): Promise<User> {
  let user = await apiFetch<User>("/auth/me");
  if (user.company_id) return user;

  const companies = await apiFetch<CompanyWithRole[]>("/companies/my");
  const company = companies.find((item) => item.selected) ?? companies.find((item) => item.is_active) ?? companies[0];

  if (!company) return user;

  await apiFetch(`/companies/${company.id}/activate`, { method: "POST" });
  user = await apiFetch<User>("/auth/me");
  return user;
}

export async function routeAfterLogin(): Promise<string> {
  const user = await ensureActiveCompany();
  return user.company_id ? "/dashboard" : "/onboarding";
}
