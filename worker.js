export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === '/api/flyers') {
      const CORS = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
      };

      if (request.method === 'OPTIONS') {
        return new Response(null, { headers: CORS });
      }

      if (request.method === 'GET') {
        const data = await env.FLYER_DATA.get('flyer-data');
        return new Response(data || '{}', {
          headers: { 'Content-Type': 'application/json', ...CORS },
        });
      }

      if (request.method === 'POST') {
        try {
          const body = await request.json();
          await env.FLYER_DATA.put('flyer-data', JSON.stringify(body));
          return new Response('{"ok":true}', {
            headers: { 'Content-Type': 'application/json', ...CORS },
          });
        } catch {
          return new Response('{"error":"invalid json"}', {
            status: 400,
            headers: { 'Content-Type': 'application/json', ...CORS },
          });
        }
      }
    }

    return env.ASSETS.fetch(request);
  },
};
