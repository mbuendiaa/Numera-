import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NUMERA_BACKEND_URL ?? "http://localhost:8000";

async function proxy(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  const target = new URL(`${BACKEND_URL}/${path.join("/")}`);
  request.nextUrl.searchParams.forEach((value, key) => target.searchParams.append(key, value));

  const headers = new Headers(request.headers);
  headers.delete("host");
  headers.delete("content-length");

  const method = request.method;
  const body = method === "GET" || method === "HEAD" ? undefined : await request.arrayBuffer();

  try {
    const response = await fetch(target, {
      method,
      headers,
      body,
      redirect: "manual",
      cache: "no-store"
    });

    return new NextResponse(response.body, {
      status: response.status,
      headers: response.headers
    });
  } catch {
    return NextResponse.json(
      {
        detail: `No se pudo conectar con el backend en ${BACKEND_URL}. Comprueba que FastAPI está arrancado.`
      },
      { status: 502 }
    );
  }
}

export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
