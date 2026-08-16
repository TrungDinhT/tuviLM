"use client";

import { Pill } from "@/components/primitives/pill";
import { useBuildLaso } from "@/lib/api/hooks";
import { describe, isApiError } from "@/lib/http/errors";

/**
 * Scaffolding, not product. Exercises the whole client path — env, headers,
 * Zod parsing, error normalization — so it is proven before any screen depends
 * on it. Delete alongside the rest of `_demo/`.
 */
export function ApiDemo() {
  const buildLaso = useBuildLaso();

  return (
    <section className="mt-8">
      <h2 className="font-display text-xl font-semibold">API client</h2>
      <p className="mt-1 text-[13px] text-muted">
        Gọi thật tới <code className="text-ink">POST /api/v1/laso/build</code>.
      </p>

      <Pill
        variant="ghost"
        className="mt-3 px-4 py-2 text-[12px]"
        disabled={buildLaso.isPending}
        onClick={() =>
          buildLaso.mutate({ calendar: "solar", year: 2009, month: 4, day: 4, hour: 5, gender: "M" })
        }
      >
        {buildLaso.isPending ? "Đang gọi…" : "Gọi /laso/build"}
      </Pill>

      {buildLaso.isError ? (
        <p className="mt-3 text-[13px] text-fire">
          {isApiError(buildLaso.error)
            ? `${describe(buildLaso.error.error)} (kind: ${buildLaso.error.error.kind})`
            : "Lỗi không xác định."}
        </p>
      ) : null}

      {buildLaso.isSuccess ? (
        <p className="mt-3 text-[13px] text-muted">
          <b className="text-ink">{buildLaso.data.ban_menh_name}</b> ·{" "}
          {Object.keys(buildLaso.data.cung_by_position).length} cung ·{" "}
          {buildLaso.data.menh_cuc_relation_label}
        </p>
      ) : null}
    </section>
  );
}
