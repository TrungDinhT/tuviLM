import { createEnv } from "@t3-oss/env-nextjs";
import { z } from "zod";

/**
 * Validated environment.
 *
 * A malformed or missing base URL fails here, at startup, naming the variable
 * — rather than surfacing later as an unexplained fetch failure in a screen.
 */
export const env = createEnv({
  client: {
    NEXT_PUBLIC_API_BASE_URL: z.url().default("http://localhost:8000"),
  },
  runtimeEnv: {
    NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL,
  },
  emptyStringAsUndefined: true,
});
