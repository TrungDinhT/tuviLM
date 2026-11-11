import { createEnv } from "@t3-oss/env-nextjs";
import { z } from "zod";

/**
 * Validated environment.
 *
 * A malformed backend URL fails here, at startup or build, naming the
 * variable, rather than surfacing later as an unexplained 404 on `/api`.
 */
export const env = createEnv({
  server: {
    /**
     * Where the FastAPI backend runs. The browser never calls it directly:
     * `next.config.ts` forwards every `/api/*` request to it, so cookies stay
     * on this site's domain. On Vercel, set it to the API service URL.
     */
    API_ORIGIN: z.url().default("http://localhost:8000"),
  },
  client: {},
  runtimeEnv: {
    API_ORIGIN: process.env.API_ORIGIN,
  },
  emptyStringAsUndefined: true,
});
