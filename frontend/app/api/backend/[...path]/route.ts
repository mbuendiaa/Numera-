import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = (process.env.NUMERA_BACKEND_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");
const PROXY_PREFIX = "/api/backend";

async function proxy(request: NextRequest) {
  // Preserve the exact path, including its trailing slash. This is important
  // for FastAPI routes such as POST /companies/, which otherwise return a 307.
  const backendPath = request.nextUrl.pathname.slice(PROXY_PREFIX.length) || "/";
  const target = new URL(`${BACKEND_URL}${backendPath}`);
  request.nextUrl.searchParams.forEach((value, key) => target.searchParams.append(key, value));

  const headers = new Headers(request.headers);
  headers.delete("host");
  headers.delete("content-length");
  headers.delete("connection");

  const method = request.method;
  const body = method === "GET" || method === "HEAD" ? undefined : await request.arrayBuffer();

  try {
    const response = await fetch(target, {
      method,
      headers,
      body,
      // Redirects are followed inside the Next.js server. They are never sent
      // to the browser as a backend URL, so the browser cannot hit a CORS error.
      redirect: "follow",
      cache: "no-store"
    });

    const responseHeaders = new Headers(response.headers);
    responseHeaders.delete("content-encoding");
    responseHeaders.delete("content-length");
    responseHeaders.delete("transfer-encoding");
    responseHeaders.delete("connection");

    return new NextResponse(response.body, {
      status: response.status,
      headers: responseHeaders
    });
  } catch (error) {
    const reason = error instanceof Error ? error.message : "Error de conexión desconocido";
    return NextResponse.json(
      {
        detail: `No se pudo conectar con el backend en ${BACKEND_URL}. Comprueba que FastAPI está arrancado. (${reason})`
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
export const OPTIONS = proxy;
