import { useQuery } from "@tanstack/react-query";
import type { StrengthWeaknessAssessment } from "@/app/_lib/types";
import { API_URL } from "@/constants/env";

async function getStrengthWeaknessAssessment({
  ownerId,
  sessionId,
}: {
  ownerId: string;
  sessionId: string;
}): Promise<StrengthWeaknessAssessment> {
  const response = await fetch(
    `${API_URL}/api/v1/sessions/${sessionId}/strength-weakness`,
    {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "X-Anonymous-Owner-Id": ownerId,
      },
      body: JSON.stringify({
        content: "Đánh giá điểm mạnh và điểm yếu của tôi.",
      }),
    },
  );

  if (!response.ok) {
    throw new Error(`Không đánh giá được điểm mạnh, điểm yếu (HTTP ${response.status})`);
  }

  const data = (await response.json()) as StrengthWeaknessAssessment;
  if (!data?.scores || !data?.score_bases || typeof data.overview !== "string") {
    throw new Error("Phản hồi điểm mạnh, điểm yếu không hợp lệ");
  }
  return data;
}

export function useStrengthWeaknessAssessment(
  ownerId: string | undefined,
  sessionId: string | undefined,
) {
  return useQuery({
    queryKey: ["strength-weakness", ownerId, sessionId],
    queryFn: () =>
      getStrengthWeaknessAssessment({
        ownerId: ownerId as string,
        sessionId: sessionId as string,
      }),
    enabled: Boolean(ownerId && sessionId),
    staleTime: Number.POSITIVE_INFINITY,
    retry: false,
  });
}
