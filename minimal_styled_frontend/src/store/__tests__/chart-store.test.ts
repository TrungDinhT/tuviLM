import { beforeEach, describe, expect, it } from 'vitest';
import { useChartStore, type BirthInput, type HistoryEntry } from '../chart-store';
import fixture from '@/lib/api/__fixtures__/build-laso.json';
import type { BuildLasoResponse, BuildSaoLuuResponse } from '@/lib/api/schemas';

const INPUT: BirthInput = { date: 14, month: 8, year: 1991, hour: 6, gender: 'F' };

function makeEntry(id: string, builtAt = Date.now()): HistoryEntry {
  return {
    id,
    builtAt,
    input: INPUT,
    response: { ...(fixture as BuildLasoResponse), id },
  };
}

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
    history: [],
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

  it('addToHistory caps at 20 entries, newest first', () => {
    const add = useChartStore.getState().addToHistory;
    for (let i = 0; i < 25; i++) add(makeEntry(`id-${i}`, 1_000 + i));
    const history = useChartStore.getState().history;
    expect(history).toHaveLength(20);
    expect(history[0]?.id).toBe('id-24');
    expect(history.at(-1)?.id).toBe('id-5');
  });

  it('addToHistory dedupes by id, refreshing position', () => {
    const add = useChartStore.getState().addToHistory;
    add(makeEntry('a', 1_000));
    add(makeEntry('b', 2_000));
    add(makeEntry('a', 3_000));
    const history = useChartStore.getState().history;
    expect(history.map((h) => h.id)).toEqual(['a', 'b']);
    expect(history[0]?.builtAt).toBe(3_000);
  });

  it('removeFromHistory drops the matching entry', () => {
    const add = useChartStore.getState().addToHistory;
    add(makeEntry('a'));
    add(makeEntry('b'));
    useChartStore.getState().removeFromHistory('a');
    expect(useChartStore.getState().history.map((h) => h.id)).toEqual(['b']);
  });

  it('loadFromHistory rehydrates current + lastInput, no API call', () => {
    const add = useChartStore.getState().addToHistory;
    add(makeEntry('a'));
    useChartStore.getState().loadFromHistory('a');
    const s = useChartStore.getState();
    expect(s.current?.id).toBe('a');
    expect(s.lastInput).toEqual(INPUT);
  });

  it('loadFromHistory on an unknown id is a no-op', () => {
    useChartStore.getState().loadFromHistory('does-not-exist');
    expect(useChartStore.getState().current).toBeNull();
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
  });
});
