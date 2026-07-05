import { beforeEach, describe, expect, it } from 'vitest';
import { useChartStore, type BirthInput } from '../chart-store';
import fixture from '@/lib/api/__fixtures__/build-laso.json';
import type { BuildLasoResponse, BuildSaoLuuResponse } from '@/lib/api/schemas';

const INPUT: BirthInput = { date: 14, month: 8, year: 1991, hour: 6, gender: 'F' };

beforeEach(() => {
  localStorage.clear();
  useChartStore.setState({
    ownerId: null,
    chartProfileId: null,
    sessionId: null,
    lastInput: null,
    current: null,
    saoLuuOverlay: null,
    selectedCungPosition: null,
  });
});

describe('useChartStore', () => {
  it('setConversationContext writes owner/profile/session ids', () => {
    useChartStore.getState().setConversationContext('anon_1', 'profile_1', 'session_1');
    expect(useChartStore.getState()).toMatchObject({
      ownerId: 'anon_1',
      chartProfileId: 'profile_1',
      sessionId: 'session_1',
    });
  });

  it('clearConversationContext keeps owner id and clears active chart/session state', () => {
    useChartStore.getState().setConversationContext('anon_1', 'profile_1', 'session_1');
    useChartStore.getState().setCurrent(INPUT, fixture as BuildLasoResponse);
    useChartStore.getState().clearConversationContext();
    expect(useChartStore.getState()).toMatchObject({
      ownerId: 'anon_1',
      chartProfileId: null,
      sessionId: null,
      lastInput: null,
      current: null,
    });
  });

  it('setCurrent writes input + response and clears overlay/selection', () => {
    useChartStore.setState({
      saoLuuOverlay: { cung_by_position: {} },
      selectedCungPosition: 'Mệnh',
    });
    useChartStore.getState().setCurrent(INPUT, fixture as BuildLasoResponse);
    const s = useChartStore.getState();
    expect(s.current?.ban_menh_name).toBe(fixture.ban_menh_name);
    expect(s.lastInput).toEqual(INPUT);
    expect(s.saoLuuOverlay).toBeNull();
    expect(s.selectedCungPosition).toBeNull();
  });

  it('clearSaoLuu resets only the overlay', () => {
    const overlay: BuildSaoLuuResponse = { cung_by_position: {} };
    useChartStore.setState({ saoLuuOverlay: overlay });
    useChartStore.getState().clearSaoLuu();
    expect(useChartStore.getState().saoLuuOverlay).toBeNull();
  });

  it('persists across rehydrate via localStorage', () => {
    useChartStore.getState().setConversationContext('anon_1', 'profile_1', 'session_1');
    useChartStore.getState().setCurrent(INPUT, fixture as BuildLasoResponse);
    const raw = localStorage.getItem('tuvilm:store:v1');
    expect(raw).not.toBeNull();
    const parsed = JSON.parse(raw!) as {
      state: {
        ownerId: string | null;
        chartProfileId: string | null;
        sessionId: string | null;
        current: BuildLasoResponse | null;
      };
    };
    expect(parsed.state.ownerId).toBe('anon_1');
    expect(parsed.state.chartProfileId).toBe('profile_1');
    expect(parsed.state.sessionId).toBe('session_1');
    expect(parsed.state.current?.ban_menh_name).toBe(fixture.ban_menh_name);
    expect(parsed.state).not.toHaveProperty('history');
  });
});
