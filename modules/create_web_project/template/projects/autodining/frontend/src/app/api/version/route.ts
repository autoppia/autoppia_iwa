// src/app/api/version/route.ts
import { NextResponse } from "next/server";
import packageJson from "../../../../package.json";

export async function GET() {
  // Priority 1: Environment variable (injected during Docker build)
  const version =
    process.env.NEXT_PUBLIC_WEB_VERSION ||
    process.env.WEB_VERSION ||
    packageJson.version ||
    "unknown";

  return NextResponse.json({ version });
}

