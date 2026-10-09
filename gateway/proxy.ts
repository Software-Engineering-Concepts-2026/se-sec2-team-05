// Vercel Routing Middleware = the gateway's login check on Vercel (ADR-014).
// docker compose does the same in web/nginx.conf with auth_request. All the logic lives in
// gateway/rules.js so `node --test` can run it; this file only hands the request over.
// Which paths run this function: "proxy.matcher" in vercel.json (API paths only, not the static pages).
// Returning undefined lets the request continue to the service chosen by the rewrites in vercel.json.
import { checkRequest } from './rules.js';

export default function proxy(request: Request) {
  return checkRequest(request);
}
