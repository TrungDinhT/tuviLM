'use client';

import { abbreviateStarStatus, cn } from '@/lib/utils';
import type { Cung, Star } from '@/lib/api/schemas';
import { isCat, isHung, getStarColorVar, getElementColorVar } from '@/features/laso-chart/lib/star-colors';

interface Props {
  cung: Cung;
  saoLuu?: Cung['saoLuu'];
  selected?: boolean;
  onClick?: () => void;
  style?: React.CSSProperties;
}

function PhuTinhGroup({
  stars,
  prefix,
  showDivider = true,
}: {
  stars: Star[];
  prefix?: string;
  showDivider?: boolean;
}) {
  if (stars.length === 0) return null;
  const cats = stars.filter(isCat);
  const hungs = stars.filter(isHung);

  return (
    <>
      {showDivider && <hr className="fc-divider" />}
      {prefix && <div className="fc-star-luu-divider">{prefix}</div>}
      <div className="fc-phu-tinh-row">
        <div className="fc-phu-tinh-col">
          {cats.map((s) => (
            <div
              key={`cat-${s.name}`}
              className="fc-star-sub"
              style={{ color: getElementColorVar(s.element) }}
            >
              {abbreviateStarStatus(s.display)}
            </div>
          ))}
        </div>
        <div className="fc-phu-tinh-col">
          {hungs.map((s) => (
            <div
              key={`hung-${s.name}`}
              className="fc-star-sub"
              style={{ color: getElementColorVar(s.element) }}
            >
              {abbreviateStarStatus(s.display)}
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

export function CungCellFull({ cung, saoLuu, selected, onClick, style }: Props) {
  return (
    <button
      type="button"
      onClick={onClick}
      style={style}
      className={cn('fc-cell', selected && 'selected', cung.is_cung_than && !selected && 'cung-than')}
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
              style={{ color: getStarColorVar(star) }}
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

      {cung.phu_tinh.length > 0 && <PhuTinhGroup stars={cung.phu_tinh} />}

      {saoLuu && saoLuu.length > 0 && (
        <PhuTinhGroup
          stars={saoLuu}
          prefix="Lưu"
          showDivider={cung.phu_tinh.length > 0}
        />
      )}

      <div className="fc-trangsinh">{cung.trang_sinh ?? 'N/A'}</div>
    </button>
  );
}
