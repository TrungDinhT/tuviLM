import { useMemo } from "react";
import type { BirthInput, Gender } from "../types";

type Props = {
  value: BirthInput;
  onChange: (next: BirthInput) => void;
  viewYear: number;
  onViewYearChange: (year: number) => void;
  onSubmit: () => void;
  onBuildSaoLuu: () => void;
  loadingBuild: boolean;
  loadingSaoLuu: boolean;
  canBuildSaoLuu: boolean;
};

function clamp(n: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, n));
}

export default function BirthForm({
  value,
  onChange,
  viewYear,
  onViewYearChange,
  onSubmit,
  onBuildSaoLuu,
  loadingBuild,
  loadingSaoLuu,
  canBuildSaoLuu,
}: Props) {
  const ageHint = useMemo(() => new Date().getFullYear() - value.year, [value.year]);

  const setField = <K extends keyof BirthInput>(key: K, fieldValue: BirthInput[K]) => {
    onChange({ ...value, [key]: fieldValue });
  };

  return (
    <section className="panel input-panel">
      <h2>Input</h2>
      <div className="grid-form">
        <label>
          Ngày
          <input
            type="number"
            min={1}
            max={31}
            value={value.date}
            onChange={(e) => setField("date", clamp(Number(e.target.value), 1, 31))}
          />
        </label>

        <label>
          Tháng
          <input
            type="number"
            min={1}
            max={12}
            value={value.month}
            onChange={(e) => setField("month", clamp(Number(e.target.value), 1, 12))}
          />
        </label>

        <label>
          Năm
          <input
            type="number"
            min={1900}
            max={2099}
            value={value.year}
            onChange={(e) => setField("year", clamp(Number(e.target.value), 1900, 2099))}
          />
        </label>

        <label>
          Năm xem
          <input
            type="number"
            min={1900}
            max={2099}
            value={viewYear}
            onChange={(e) => onViewYearChange(clamp(Number(e.target.value), 1900, 2099))}
          />
        </label>

        <label>
          Giờ
          <input
            type="number"
            min={0}
            max={23}
            value={value.hour}
            onChange={(e) => setField("hour", clamp(Number(e.target.value), 0, 23))}
          />
        </label>

        <label>
          Giới tính
          <select
            value={value.gender}
            onChange={(e) => setField("gender", e.target.value as Gender)}
          >
            <option value="M">Nam</option>
            <option value="F">Nữ</option>
          </select>
        </label>
      </div>

      <p className="hint">Tuổi ước tính: {ageHint}</p>

      <div className="input-actions">
        <button className="primary-btn" onClick={onSubmit} disabled={loadingBuild || loadingSaoLuu}>
          {loadingBuild ? "Đang lập lá số..." : "Lập lá số"}
        </button>
        <button
          className="primary-btn"
          onClick={onBuildSaoLuu}
          disabled={!canBuildSaoLuu || loadingBuild || loadingSaoLuu}
        >
          {loadingSaoLuu ? "Đang an sao lưu..." : "An sao lưu"}
        </button>
      </div>
    </section>
  );
}
