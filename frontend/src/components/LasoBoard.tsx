import type { LasoData } from "../types";

type Props = {
  laso: LasoData | null;
  selectedPosition: string | null;
  onSelectPosition: (position: string) => void;
};

const GRID: Array<Array<string | null>> = [
  ["Tị", "Ngọ", "Mùi", "Thân"],
  ["Thìn", null, null, "Dậu"],
  ["Mão", null, null, "Tuất"],
  ["Dần", "Sửu", "Tý", "Hợi"]
];

const STAR_COLORS: Record<string, string> = {
  "Tử Vi": "#b8860b",
  "Thiên Phủ": "#b8860b",
  "Thái Dương": "#de5227",
  "Vũ Khúc": "#6b7280",
  "Liêm Trinh": "#de5227",
  "Thất Sát": "#6b7280",
  "Tham Lang": "#1f4f8b",
  "Phá Quân": "#1f4f8b",
  "Thiên Đồng": "#1f4f8b",
  "Thiên Cơ": "#1d7d4f",
  "Thái Âm": "#1f4f8b",
  "Thiên Lương": "#1d7d4f",
  "Cự Môn": "#1f4f8b",
  "Thiên Tướng": "#1f4f8b"
};

const ELEMENT_COLORS: Record<string, string> = {
  "Kim": "#808080",
  "Mộc": "#008000",
  "Thủy": "#00008B",
  "Hỏa": "#FF0000",
  "Thổ": "#B8860B"
};

function colorByStarName(starWithStatus: string): string {
  const baseName = starWithStatus.split(" (")[0];
  return STAR_COLORS[baseName] ?? "#374151";
}

export default function LasoBoard({ laso, selectedPosition, onSelectPosition }: Props) {
  return (
    <section className="panel laso-panel">
      <div className="section-head">
        <h2>Lá số</h2>
        <span className="summary">{laso?.summary ?? "Chưa có dữ liệu"}</span>
      </div>

      <div className="laso-grid">
        {GRID.flat().map((position, idx) => {
          const row = Math.floor(idx / 4) + 1;
          const col = (idx % 4) + 1;

          if (position === null) {
            if (idx === 6 || idx === 9 || idx === 10) {
              return null;
            }
            if (idx === 5) {
              return (
                <div
                  key={`center-${idx}`}
                  className="center-cell"
                  style={{ gridRow: "2 / span 2", gridColumn: "2 / span 2" }}
                >
                  {laso ? (
                    <div className="center-info">
                      <p className="center-line">Bản mệnh: {laso.banMenhName}</p>
                      <p className="center-line">Cục: {laso.cucName}</p>
                      <p className="center-line">{laso.menhCucRelationLabel}</p>
                    </div>
                  ) : (
                    <>
                      <p>TUVI LM</p>
                      <p className="center-sub">interactive board</p>
                    </>
                  )}
                </div>
              );
            }
            return (
              <div
                key={`empty-${idx}`}
                className="empty-cell"
                style={{ gridRowStart: row, gridColumnStart: col }}
              />
            );
          }

          const cung = laso?.cungByPosition[position];
          return (
            <button
              key={position}
              className={`cung-card ${selectedPosition === position ? "active" : ""}`}
              style={{ gridRowStart: row, gridColumnStart: col }}
              onClick={() => onSelectPosition(position)}
              disabled={!cung}
            >
              {cung ? (
                <div className="cung-content">
                  <p className="age-dai-van">{cung.ageDaiVan ?? "N/A"}</p>

                  {(cung.isTuan || cung.isTriet) && (
                    <p className="star-flags top-center">
                      {cung.isTuan ? "Tuần " : ""}
                      {cung.isTriet ? "Triệt" : ""}
                    </p>
                  )}

                  <h3>{cung.role}{cung.isCungThan ? " - Thân" : ""} ({cung.position})</h3>

                  <div className="main-tuhoa-row">
                    <div className="main-stars-col">
                      {cung.chinhTinh.map((star) => (
                        <p key={star} className="star-main" style={{ color: colorByStarName(star) }}>
                          {star}
                        </p>
                      ))}
                    </div>

                    <div className="tuhoa-col">
                      {cung.tuhoa.map((item) => (
                        <p key={item.name} className="star-tuhoa">{item.display}</p>
                      ))}
                    </div>
                  </div>

                  <hr />

                  {cung.phuTinh.map((star) => (
                    <p
                      key={`${star.name}-${star.display}`}
                      className="star-sub"
                      style={{ color: ELEMENT_COLORS[star.element] ?? "#374151" }}
                    >
                      {star.display}
                    </p>
                  ))}

                  {cung.saoLuu.length > 0 && (
                    <>
                      <p className="star-luu-divider">--Lưu--</p>
                      {cung.saoLuu.map((star) => (
                        <p
                          key={`luu-${star.name}-${star.display}`}
                          className="star-sub"
                          style={{ color: ELEMENT_COLORS[star.element] ?? "#374151" }}
                        >
                          {star.display}
                        </p>
                      ))}
                    </>
                  )}

                  <p className="star-trangsinh bottom-center">Tràng Sinh: {cung.trangSinh ?? "N/A"}</p>
                </div>
              ) : (
                <p>{position}</p>
              )}
            </button>
          );
        })}
      </div>
    </section>
  );
}
