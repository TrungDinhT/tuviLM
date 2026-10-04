export const apiEndpoints = {
  accountAccess: "/api/v1/me",
  redeemCode: "/api/v1/account/redeem-code",
  buildLaso: "/api/v1/laso/build",
  previewLaso: "/api/v1/laso/preview",
  anonymous: "/api/v1/anonymous",
  chartProfiles: "/api/v1/chart-profiles",
  chartProfile: (id: string) => `/api/v1/chart-profiles/${encodeURIComponent(id)}`,
  profileSessions: (profileId: string) =>
    `/api/v1/chart-profiles/${encodeURIComponent(profileId)}/sessions`,
  session: (id: string) => `/api/v1/sessions/${encodeURIComponent(id)}`,
  chatStream: (sessionId: string) =>
    `/api/v1/sessions/${encodeURIComponent(sessionId)}/chat/stream`,
} as const;
