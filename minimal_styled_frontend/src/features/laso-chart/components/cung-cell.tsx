'use client';

import { abbreviateStarStatus, cn } from '@/lib/utils';
import type { Cung, Star } from '@/lib/api/schemas';

interface Props {
  cung: Cung;
  saoLuu?: Cung['saoLuu'];
  selected?: boolean;
  onClick?: () => void;
  style?: React.CSSProperties;
  variant?: 'compact' | 'full';
}

function isCat(star: Star) {
  return star.sao_type?.includes('Cát') ?? true;
}

function isHung(star: Star) {
  return star.sao_type?.includes('Hung') ?? false;
}

const STAR_COLORS: Record<string, string> = {
  'Tử Vi': '#B8860B',
  'Thiên Phủ': '#B8860B',
  'Thái Dương': '#FF0000',
  'Vũ Khúc': '#808080',
  'Liêm Trinh': '#FF0000',
  'Thất Sát': '#808080',
  'Tham Lang': '#00008B',
  'Phá Quân': '#00008B',
  'Thiên Đồng': '#00008B',
  'Thiên Cơ': '#008000',
  'Thái Âm': '#00008B',
  'Thiên Lương': '#008000',
  'Cự Môn': '#00008B',
  'Thiên Tướng': '#00008B',
};

const ELEMENT_COLORS: Record<string, string> = {
  Kim: '#808080',
  Mộc: '#008000',
  Thủy: '#00008B',
  Hỏa: '#FF0000',
  Thổ: '#B8860B',
};

function colorByStarName(starWithStatus: string): string {
  const baseName = starWithStatus.split(' (')[0] ?? '';
  return STAR_COLORS[baseName] ?? '#374151';
}

export function CungCell({ cung, saoLuu, selected, onClick, style, variant = 'compact' }: Props) {
  const isFull = variant === 'full';

  if (isFull) {
    return (
      <button
        type="button"
        onClick={onClick}
        style={style}
        className={cn(
          'fc-cell',
          selected && 'selected',
          cung.is_cung_than && !selected && 'cung-than',
        )}
      >
        {typeof cung.age_daivan === 'number' && (
          <span className="fc-age">{cung.age_daivan}</span>
        )}

        <div className="fc-role">
          {cung.role}
          {cung.is_cung_than ? ' - Thân' : ''} ({cung.position})
        </div>

        <div className="fc-main-tuhoa-row">
          <div className="fc-main-stars-col">
            {cung.chinh_tinh.map((star) => (
              <div
                key={star}
                className="fc-star-main"
                style={{ color: colorByStarName(star) }}
              >
                {abbreviateStarStatus(star)}
              </div>
            ))}
          </div>
          <div className="fc-tuhoa-col">
            {cung.tuhoa.map((t) => (
              <div key={t.name} className="fc-star-tuhoa">
                {t.display}
              </div>
            ))}
          </div>
        </div>

        {cung.phu_tinh.length > 0 && (
          <>
            <hr className="fc-divider" />
            <div className="fc-phu-tinh-row">
              <div className="fc-phu-tinh-col">
                {cung.phu_tinh.filter(isCat).map((s) => (
                  <div
                    key={`${s.name}-${s.display}`}
                    className="fc-star-sub"
                    style={{ color: ELEMENT_COLORS[s.element] ?? '#374151' }}
                  >
                    {abbreviateStarStatus(s.display)}
                  </div>
                ))}
              </div>
              <div className="fc-phu-tinh-col">
                {cung.phu_tinh.filter(isHung).map((s) => (
                  <div
                    key={`${s.name}-${s.display}`}
                    className="fc-star-sub"
                    style={{ color: ELEMENT_COLORS[s.element] ?? '#374151' }}
                  >
                    {abbreviateStarStatus(s.display)}
                  </div>
                ))}
              </div>
            </div>
          </>
        )}

        {saoLuu && saoLuu.length > 0 && (
          <>
            {cung.phu_tinh.length > 0 && <hr className="fc-divider" />}
            <div className="fc-star-luu-divider">
              Lưu
            </div>
            <div className="fc-phu-tinh-row">
              <div className="fc-phu-tinh-col">
                {saoLuu.filter(isCat).map((s) => (
                  <div
                    key={`luu-${s.name}-${s.display}`}
                    className="fc-star-sub"
                    style={{ color: ELEMENT_COLORS[s.element] ?? '#374151' }}
                  >
                    {abbreviateStarStatus(s.display)}
                  </div>
                ))}
              </div>
              <div className="fc-phu-tinh-col">
                {saoLuu.filter(isHung).map((s) => (
                  <div
                    key={`luu-${s.name}-${s.display}`}
                    className="fc-star-sub"
                    style={{ color: ELEMENT_COLORS[s.element] ?? '#374151' }}
                  >
                    {abbreviateStarStatus(s.display)}
                  </div>
                ))}
              </div>
            </div>
          </>
        )}

        <div className="fc-trangsinh">{cung.trang_sinh ?? 'N/A'}</div>
      </button>
    );
  }

  return (
    <button
      type="button"
      onClick={onClick}
      style={style}
      className={cn(
        'flex min-w-0 flex-col gap-1 overflow-hidden bg-card p-1 text-left',
        selected && 'ring-2 ring-inset ring-primary',
      )}
    >
      <div className="text-[10px] leading-tight font-medium text-primary">
        {cung.position}
      </div>

      {cung.chinh_tinh.length > 0 && (
        <div className="mt-0.5 flex flex-col gap-0.5 text-center">
          {cung.chinh_tinh.map((star) => (
            <div
              key={star}
              className="leading-tight font-medium text-foreground"
              style={{ fontSize: '9px' }}
            >
              {abbreviateStarStatus(star)}
            </div>
          ))}
        </div>
      )}
    </button>
  );
}
