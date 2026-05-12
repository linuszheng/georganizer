// Cloudflare Pages Function for /api/flyers
// Uses KV namespace "FLYER_DATA" (bind in Cloudflare dashboard or wrangler.toml)
// KV key: "flyer-data"

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json', ...CORS_HEADERS },
  });
}

export async function onRequestOptions() {
  return new Response(null, { headers: CORS_HEADERS });
}

export async function onRequestGet(context) {
  const data = await context.env.FLYER_DATA.get('flyer-data');
  return json(data ? JSON.parse(data) : {});
}

export async function onRequestPost(context) {
  try {
    const body = await context.request.json();
    await context.env.FLYER_DATA.put('flyer-data', JSON.stringify(body));
    return json({ ok: true });
  } catch (e) {
    return json({ error: 'invalid json' }, 400);
  }
}
