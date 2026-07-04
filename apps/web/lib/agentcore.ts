import { BedrockAgentCoreClient, InvokeAgentRuntimeCommand } from "@aws-sdk/client-bedrock-agentcore";
import { fromWebToken, fromNodeProviderChain, fromEnv } from "@aws-sdk/credential-providers";

const REGION = process.env.AWS_REGION ?? "us-east-1";
const AGENT_RUNTIME_ARN = process.env.AI_HYPE_CHECKER_RUNTIME_ARN ?? "";

let _client: BedrockAgentCoreClient | null = null;

function client(): BedrockAgentCoreClient {
  if (_client) return _client;

  const roleArn = process.env.AWS_ROLE_ARN;
  const oidcToken = process.env.AWS_WEB_IDENTITY_TOKEN ?? process.env.VERCEL_OIDC_TOKEN;

  let credentials;
  if (roleArn && oidcToken) {
    credentials = fromWebToken({
      roleArn,
      webIdentityToken: oidcToken,
      roleSessionName: "ai-hype-checker-web",
      durationSeconds: 3600,
    });
  } else if (process.env.AWS_ACCESS_KEY_ID && process.env.AWS_SECRET_ACCESS_KEY) {
    credentials = fromEnv();
  } else {
    credentials = fromNodeProviderChain();
  }

  _client = new BedrockAgentCoreClient({ region: REGION, credentials });
  return _client;
}

export type Verdict = "hype" | "exaggerated" | "grounded" | "failed";

export interface JudgeResult {
  score: number | null;
  verdict: Verdict;
  reasons: string[];
  flagged_phrases: string[];
}

export interface InvokeResult {
  status: "OK" | "ERROR";
  result?: JudgeResult;
  error?: string;
}

async function readResponseBody(response: unknown): Promise<string> {
  // AWS SDK の streaming blob payload は実行環境ごとに実体が異なる
  // (Web ReadableStream / Node.js Readable / Uint8Array)。
  // @smithy/util-stream が生やす transformToString() が環境差を吸収してくれる。
  const withHelper = response as { transformToString?: (encoding?: string) => Promise<string> };
  if (typeof withHelper.transformToString === "function") {
    return withHelper.transformToString("utf-8");
  }

  const maybeStream = response as { getReader?: () => unknown };
  const chunks: Uint8Array[] = [];
  if (typeof maybeStream.getReader === "function") {
    const reader = (response as ReadableStream<Uint8Array>).getReader();
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      if (value) chunks.push(value);
    }
  } else {
    chunks.push(response as Uint8Array);
  }
  const totalLen = chunks.reduce((sum, c) => sum + c.byteLength, 0);
  const merged = new Uint8Array(totalLen);
  let offset = 0;
  for (const c of chunks) {
    merged.set(c, offset);
    offset += c.byteLength;
  }
  return new TextDecoder().decode(merged);
}

export async function judgePost(text: string, lang: string = "ja"): Promise<InvokeResult> {
  if (!AGENT_RUNTIME_ARN) {
    return { status: "ERROR", error: "AI_HYPE_CHECKER_RUNTIME_ARN 未設定" };
  }
  const body = new TextEncoder().encode(JSON.stringify({ text, lang }));
  const runtimeSessionId = `web-${crypto.randomUUID()}-${Date.now()}`;
  try {
    const cmd = new InvokeAgentRuntimeCommand({
      agentRuntimeArn: AGENT_RUNTIME_ARN,
      runtimeSessionId,
      payload: body,
      contentType: "application/json",
      accept: "application/json",
    });
    const resp = await client().send(cmd);
    if (!resp.response) return { status: "ERROR", error: "empty response" };
    const raw = await readResponseBody(resp.response);
    const parsed = JSON.parse(raw) as JudgeResult;
    return { status: "OK", result: parsed };
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e);
    return { status: "ERROR", error: msg };
  }
}
