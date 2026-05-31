import type { CungPayload } from "../_lib/types";
import { DefaultPanels } from "./DefaultPanels";
import { CungDetailCard } from "./CungDetailCard";
import { SaoDetailCard } from "./SaoDetailCard";

interface RightRailProps {
  selectedCung: CungPayload | null;
  selectedSao: string | null;
  onCloseCung: () => void;
  onCloseSao: () => void;
  onSaoClick: (saoName: string) => void;
}

export function RightRail({
  selectedCung,
  selectedSao,
  onCloseCung,
  onCloseSao,
  onSaoClick,
}: RightRailProps) {
  return (
    <div className="relative h-full">
      {selectedCung ? (
        <CungDetailCard cung={selectedCung} onSaoClick={onSaoClick} onClose={onCloseCung} />
      ) : (
        <DefaultPanels />
      )}
      {selectedSao && <SaoDetailCard saoName={selectedSao} onClose={onCloseSao} />}
    </div>
  );
}
