import { describe, expect, it, vi } from 'vitest';
import { chatWithResync } from '../hooks';
import { NO_LASO_SENTINEL } from '../schemas';
import type { BuildLasoRequest, BuildLasoResponse, ChatResponse } from '../schemas';
import { isApiError } from '@/lib/http/errors';

const INPUT: BuildLasoRequest = {
  date: 14,
  month: 8,
  year: 1991,
  hour: 6,
  gender: 'F',
};

function makeBuildResponse(): BuildLasoResponse {
  return {
    id: 'build-1',
    summary: '',
    ban_menh_name: 'X',
    cuc_name: 'Y',
    menh_cuc_relation_label: 'Z',
    cung_by_position: {},
  };
}

describe('chatWithResync', () => {
  it('returns the first response when answer is real', async () => {
    const real: ChatResponse = { answer: 'Câu trả lời thật', tool_calls: [] };
    const chat = vi.fn().mockResolvedValueOnce(real);
    const buildLaso = vi.fn();
    const apply = vi.fn();

    const result = await chatWithResync(
      { message: 'hi', lastInput: INPUT, applyBuildResponse: apply },
      { chat, buildLaso },
    );

    expect(result).toEqual(real);
    expect(chat).toHaveBeenCalledTimes(1);
    expect(buildLaso).not.toHaveBeenCalled();
    expect(apply).not.toHaveBeenCalled();
  });

  it('rebuilds and retries when first answer is the sentinel', async () => {
    const sentinel: ChatResponse = { answer: NO_LASO_SENTINEL, tool_calls: [] };
    const real: ChatResponse = { answer: 'OK', tool_calls: [] };
    const chat = vi
      .fn()
      .mockResolvedValueOnce(sentinel)
      .mockResolvedValueOnce(real);
    const build = makeBuildResponse();
    const buildLaso = vi.fn().mockResolvedValue(build);
    const apply = vi.fn();
    const onResync = vi.fn();

    const result = await chatWithResync(
      { message: 'hi', lastInput: INPUT, applyBuildResponse: apply, onResync },
      { chat, buildLaso },
    );

    expect(result).toEqual(real);
    expect(chat).toHaveBeenCalledTimes(2);
    expect(buildLaso).toHaveBeenCalledTimes(1);
    expect(buildLaso).toHaveBeenCalledWith(INPUT);
    expect(apply).toHaveBeenCalledWith(build);
    expect(onResync).toHaveBeenCalledTimes(1);
  });

  it('throws no-la-so requiresRebuild=true when sentinel and lastInput is null', async () => {
    const sentinel: ChatResponse = { answer: NO_LASO_SENTINEL, tool_calls: [] };
    const chat = vi.fn().mockResolvedValueOnce(sentinel);
    const buildLaso = vi.fn();
    const apply = vi.fn();

    await expect(
      chatWithResync(
        { message: 'hi', lastInput: null, applyBuildResponse: apply },
        { chat, buildLaso },
      ),
    ).rejects.toMatchObject({ kind: 'no-la-so', requiresRebuild: true });

    expect(chat).toHaveBeenCalledTimes(1);
    expect(buildLaso).not.toHaveBeenCalled();
  });

  it('throws no-la-so requiresRebuild=false when sentinel persists after rebuild', async () => {
    const sentinel: ChatResponse = { answer: NO_LASO_SENTINEL, tool_calls: [] };
    const chat = vi
      .fn()
      .mockResolvedValueOnce(sentinel)
      .mockResolvedValueOnce(sentinel);
    const buildLaso = vi.fn().mockResolvedValue(makeBuildResponse());
    const apply = vi.fn();

    const promise = chatWithResync(
      { message: 'hi', lastInput: INPUT, applyBuildResponse: apply },
      { chat, buildLaso },
    );

    await expect(promise).rejects.toSatisfy(
      (err) => isApiError(err) && err.kind === 'no-la-so' && err.requiresRebuild === false,
    );
    expect(chat).toHaveBeenCalledTimes(2);
    expect(buildLaso).toHaveBeenCalledTimes(1);
  });
});
