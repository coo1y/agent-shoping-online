import { NextResponse } from "next/server";

const BACKEND_URL =
  process.env.BACKEND_URL ?? process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://127.0.0.1:8000";

export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  const bodyText = await request.text();

  let upstream: Response;
  try {
    upstream = await fetch(`${BACKEND_URL}/api/chat/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: bodyText,
      cache: "no-store",
    });
  } catch (e: any) {
    return NextResponse.json(
      {
        error: "Failed to reach backend",
        backend_url: BACKEND_URL,
        message: e?.message ?? String(e),
      },
      { status: 502 }
    );
  }

  if (!upstream.ok) {
    const text = await upstream.text().catch(() => "");
    return NextResponse.json(
      {
        error: "Backend returned an error",
        status: upstream.status,
        body: text,
      },
      { status: upstream.status }
    );
  }

  return new Response(upstream.body, {
    status: upstream.status,
    headers: {
      "Content-Type": upstream.headers.get("content-type") ?? "text/plain; charset=utf-8",
      "Cache-Control": "no-store",
    },
  });
}
