import type { CauPhuResponse, CungPayload } from "../_lib/types";
import { DefaultPanels } from "./DefaultPanels";
import { CungDetailCard } from "./CungDetailCard";
import { SaoDetailCard } from "./SaoDetailCard";

interface RightRailProps {
  selectedCung: CungPayload | null;
  selectedSao: string | null;
  cauPhu?: CauPhuResponse;
  onCloseCung: () => void;
  onCloseSao: () => void;
  onSaoClick: (saoName: string) => void;
}

export function RightRail({
  selectedCung,
  selectedSao,
  cauPhu,
  onCloseCung,
  onCloseSao,
  onSaoClick,
}: RightRailProps) {
  return (
    <div className="relative h-full">
      {selectedCung ? (
        <CungDetailCard cung={selectedCung} onSaoClick={onSaoClick} onClose={onCloseCung} />
      ) : (
        <DefaultPanels cauPhu={cauPhu} />
      )}
      {selectedSao && <SaoDetailCard saoName={selectedSao} onClose={onCloseSao} />}
    </div>
  );
}
