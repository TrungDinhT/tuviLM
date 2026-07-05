'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { ChevronRight, MessageSquare, Plus, Trash2 } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import {
  useChartProfiles,
  useDeleteChartProfile,
  useDeleteSession,
  useOpenChartSession,
  useSessions,
} from '@/lib/api/hooks';
import { apiErrorMessage } from '@/lib/http/errors';
import { cn } from '@/lib/utils';
import { useChartStore } from '@/store/chart-store';

function formatRelative(ms: number, now: number): string {
  const diff = Math.max(0, now - ms);
  const min = Math.floor(diff / 60_000);
  if (min < 1) return 'Vừa xong';
  if (min < 60) return `${min} phút trước`;
  const hr = Math.floor(min / 60);
  if (hr < 24) return `${hr} giờ trước`;
  const day = Math.floor(hr / 24);
  if (day < 30) return `${day} ngày trước`;
  return `${Math.floor(day / 30)} tháng trước`;
}

interface ConversationSwitcherProps {
  variant?: 'card' | 'sidebar';
}

export function ConversationSwitcher({ variant = 'card' }: ConversationSwitcherProps) {
  const router = useRouter();
  const ownerId = useChartStore((s) => s.ownerId);
  const chartProfileId = useChartStore((s) => s.chartProfileId);
  const sessionId = useChartStore((s) => s.sessionId);
  const setConversationContext = useChartStore((s) => s.setConversationContext);
  const clearConversationContext = useChartStore((s) => s.clearConversationContext);
  const setCurrent = useChartStore((s) => s.setCurrent);
  const profilesQuery = useChartProfiles(ownerId);
  const openChartSession = useOpenChartSession();
  const deleteChartProfile = useDeleteChartProfile();
  const deleteSession = useDeleteSession();
  const [now] = useState(() => Date.now());
  const [expandedProfileId, setExpandedProfileId] = useState<string | null>(null);
  const isCard = variant === 'card';
  const profiles = [...(profilesQuery.data?.chart_profiles ?? [])].sort(
    (a, b) => Date.parse(b.updated_at) - Date.parse(a.updated_at),
  );
  const fallbackProfileId = profiles.some((profile) => profile.id === chartProfileId)
    ? chartProfileId
    : profiles[0]?.id ?? null;
  const openProfileId = profiles.some((profile) => profile.id === expandedProfileId)
    ? expandedProfileId
    : fallbackProfileId;
  const openProfile = profiles.find((profile) => profile.id === openProfileId) ?? null;
  const sessionsQuery = useSessions(ownerId, openProfile?.id ?? null);
  const sessions = sessionsQuery.data?.sessions ?? [];
  const isMutating =
    openChartSession.isPending || deleteChartProfile.isPending || deleteSession.isPending;

  if (!ownerId) {
    const content = (
      <>
        <div className="flex items-center justify-between gap-2">
          <div className="text-sm font-medium">Hồ sơ</div>
          <Button asChild size="xs" variant="outline">
            <Link href="/">
              <Plus className="size-3" />
              Lá số
            </Link>
          </Button>
        </div>
        <div className="text-xs text-muted-foreground">
          An lại lá số để tạo phiên trò chuyện backend.
        </div>
      </>
    );
    return isCard ? (
      <Card size="sm">
        <CardContent className="flex flex-col gap-3">{content}</CardContent>
      </Card>
    ) : (
      <div className="flex flex-col gap-3 px-2 py-3">{content}</div>
    );
  }

  const openSession = (nextSessionId: string | null) => {
    if (!openProfile) return;
    openChartSession.mutate(
      { ownerId, profile: openProfile, sessionId: nextSessionId },
      {
        onSuccess: (result) => {
          setConversationContext(result.ownerId, result.chartProfileId, result.sessionId);
          setCurrent(result.input, result.response);
          router.push('/chat');
        },
      },
    );
  };

  const removeProfile = (profileId: string, name: string) => {
    if (!window.confirm(`Xóa toàn bộ hồ sơ "${name}" và các phiên trò chuyện?`)) return;
    deleteChartProfile.mutate(
      { ownerId, chartProfileId: profileId },
      {
        onSuccess: () => {
          if (chartProfileId === profileId) clearConversationContext();
          setExpandedProfileId((current) => (current === profileId ? null : current));
        },
      },
    );
  };

  const removeSession = (removedSessionId: string) => {
    if (!openProfile) return;
    if (!window.confirm('Xóa phiên trò chuyện này?')) return;
    deleteSession.mutate(
      { ownerId, chartProfileId: openProfile.id, sessionId: removedSessionId },
      {
        onSuccess: () => {
          if (sessionId === removedSessionId) clearConversationContext();
        },
      },
    );
  };

  const content = (
    <>
      <div className="flex items-center justify-between gap-2">
        <div className="text-sm font-medium">Hồ sơ</div>
        <Button asChild size="xs" variant="outline">
          <Link href="/">
            <Plus className="size-3" />
            Lá số
          </Link>
        </Button>
      </div>

      {profilesQuery.isPending ? (
        <div className="text-xs text-muted-foreground">Đang tải hồ sơ...</div>
      ) : profilesQuery.isError ? (
        <div className="text-xs text-destructive" role="alert">
          {apiErrorMessage(profilesQuery.error)}
        </div>
      ) : profiles.length === 0 ? (
        <div className="text-xs text-muted-foreground">Chưa có hồ sơ lá số.</div>
      ) : (
        <div className="custom-scrollbar flex max-h-[30rem] flex-col gap-1 overflow-y-auto pr-1">
          {profiles.map((profile) => {
            const expanded = profile.id === openProfileId;
            const currentProfile = profile.id === chartProfileId;
            const profileName = profile.display_name.trim() || 'Không tên';
            return (
              <section key={profile.id} className="flex flex-col">
                <div className="flex items-stretch gap-1">
                  <Button
                    type="button"
                    variant={expanded ? 'secondary' : 'ghost'}
                    size="sm"
                    className="h-auto min-w-0 flex-1 justify-start gap-2 px-2 py-2 text-left"
                    onClick={() => setExpandedProfileId(expanded ? null : profile.id)}
                  >
                    <ChevronRight
                      className={cn('size-3.5 shrink-0 transition-transform', expanded && 'rotate-90')}
                    />
                    <span className="min-w-0 flex-1">
                      <span className="block truncate text-sm font-medium">{profileName}</span>
                      <span className="block truncate text-[11px] text-muted-foreground">
                        {profile.birth_info.day}/{profile.birth_info.month}/{profile.birth_info.year} ·{' '}
                        {formatRelative(Date.parse(profile.updated_at), now)}
                      </span>
                    </span>
                    {currentProfile ? (
                      <Badge variant="secondary" className="shrink-0 text-[10px]">
                        Đang xem
                      </Badge>
                    ) : null}
                  </Button>
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon-sm"
                    aria-label={`Xóa hồ sơ ${profileName}`}
                    disabled={isMutating}
                    onClick={() => removeProfile(profile.id, profileName)}
                  >
                    <Trash2 className="size-3.5" />
                  </Button>
                </div>

                {expanded ? (
                  <div className="ml-5 mt-1 flex flex-col gap-1 border-l border-border pl-2">
                    <Button
                      type="button"
                      variant="outline"
                      size="xs"
                      className="justify-start"
                      disabled={isMutating}
                      onClick={() => openSession(null)}
                    >
                      <Plus className="size-3" />
                      Phiên mới
                    </Button>

                    {sessionsQuery.isPending ? (
                      <div className="px-2 py-1 text-xs text-muted-foreground">Đang tải phiên...</div>
                    ) : sessionsQuery.isError ? (
                      <div className="px-2 py-1 text-xs text-destructive" role="alert">
                        {apiErrorMessage(sessionsQuery.error)}
                      </div>
                    ) : sessions.length === 0 ? (
                      <div className="px-2 py-1 text-xs text-muted-foreground">Chưa có phiên.</div>
                    ) : (
                      sessions.map((session) => {
                        const isActiveSession = sessionId === session.id;
                        const sessionTitle = session.title?.trim() || 'Phiên trò chuyện';
                        return (
                          <div key={session.id} className="flex items-stretch gap-1">
                            <Button
                              type="button"
                              variant={isActiveSession ? 'secondary' : 'ghost'}
                              size="sm"
                              className="h-auto min-w-0 flex-1 justify-start gap-2 px-2 py-1.5 text-left"
                              disabled={isMutating}
                              onClick={() => openSession(session.id)}
                            >
                              <MessageSquare className="size-3.5 shrink-0" />
                              <span className="min-w-0 flex-1">
                                <span className="block truncate">{sessionTitle}</span>
                                <span className="block truncate text-[11px] text-muted-foreground">
                                  {formatRelative(Date.parse(session.updated_at), now)} ·{' '}
                                  {session.message_count} tin nhắn
                                </span>
                              </span>
                            </Button>
                            <Button
                              type="button"
                              variant="ghost"
                              size="icon-sm"
                              aria-label={`Xóa phiên ${sessionTitle}`}
                              disabled={isMutating}
                              onClick={() => removeSession(session.id)}
                            >
                              <Trash2 className="size-3.5" />
                            </Button>
                          </div>
                        );
                      })
                    )}
                  </div>
                ) : null}
              </section>
            );
          })}
        </div>
      )}

      {openChartSession.isError ? (
        <div className="text-xs text-destructive" role="alert">
          {apiErrorMessage(openChartSession.error)}
        </div>
      ) : null}
    </>
  );

  return isCard ? (
    <Card size="sm">
      <CardContent className="flex flex-col gap-3">{content}</CardContent>
    </Card>
  ) : (
    <div
      className={cn(
        'flex min-h-0 flex-1 flex-col gap-3 overflow-y-auto rounded-lg border border-sidebar-border bg-sidebar-accent/20 p-2',
      )}
    >
      {content}
    </div>
  );
}
