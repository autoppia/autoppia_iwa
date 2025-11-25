// src/app/api/log-event/route.ts

import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.API_URL || "http://app:8080";

interface LogEventRequestBody {
  event_name: string;
  user_id?: string | null;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  data?: Record<string, any>;
}

export async function POST(req: NextRequest) {
  let body: LogEventRequestBody;

  // 1) Validar y parsear JSON
  try {
    const ct = req.headers.get("content-type") || "";
    if (!ct.includes("application/json")) {
      return NextResponse.json(
        { success: false, error: "Invalid Content-Type" },
        { status: 400 }
      );
    }

    const raw = await req.text();
    if (!raw) {
      return NextResponse.json(
        { success: false, error: "Empty request body" },
        { status: 400 }
      );
    }

    body = JSON.parse(raw);
  } catch (err) {
    console.error("Error parsing request body:", err);
    return NextResponse.json(
      { success: false, error: "Invalid JSON input" },
      { status: 400 }
    );
  }

  // 2) Construir el evento
  const webAgentId = req.headers.get("X-WebAgent-Id") || "1";
  const validatorId=req.headers.get("X-Validator-Id") || "1";
  const { event_name, user_id = null, data = {} } = body;

  const newEntry = {
    event_name,
    web_agent_id: webAgentId,
    user_id,
    data,
    timestamp: new Date().toISOString(),
    validator_id: validatorId,
  };

  const externalPayload = {
    web_agent_id: webAgentId,
    web_url: req.headers.get("referer") || null,
    data: newEntry,
    validator_id: validatorId,
  };

  // 3) Enviar al backend real
  try {
    const res = await fetch(`${BACKEND_URL}/save_events/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(externalPayload),
    });

    if (!res.ok) {
      const errText = await res.text();
      console.error("❌ Backend error:", res.status, errText);
      return NextResponse.json(
        { success: false, error: `Backend error: ${res.status}` },
        { status: 502 }
      );
    }
  } catch (err) {
    console.error("❌ Failed to forward event to backend:", err);
    return NextResponse.json(
      { success: false, error: "Failed to forward event" },
      { status: 502 }
    );
  }

  // 4) Responder éxito
  return NextResponse.json({ success: true });
}

export async function GET() {
  return NextResponse.json({ logs: [], message: "File logging is disabled" });
}

export async function DELETE() {
  return NextResponse.json({
    success: true,
    message: "Event log deletion is disabled",
  });
}
