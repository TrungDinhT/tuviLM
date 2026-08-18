import type { CungPayload, UserProfile } from "../_lib/types";
import { DefaultPanels } from "./DefaultPanels";
import { CungDetailCard } from "./CungDetailCard";
import { SaoDetailCard } from "./SaoDetailCard";

interface RightRailProps {
  profile: UserProfile;
  selectedCung: CungPayload | null;
  selectedSao: string | null;
  onCloseCung: () => void;
  onCloseSao: () => void;
  onSaoClick: (saoName: string) => void;
}

export function RightRail({
  profile,
  selectedCung,
  selectedSao,
  onCloseCung,
  onCloseSao,
  onSaoClick,
}: RightRailProps) {
  return (
    <div className="relative h-full overflow-y-auto pr-1">
      {selectedCung ? (
        <CungDetailCard cung={selectedCung} onSaoClick={onSaoClick} onClose={onCloseCung} />
      ) : (
        <DefaultPanels profile={profile} />
      )}
      {selectedSao && <SaoDetailCard saoName={selectedSao} onClose={onCloseSao} />}
    </div>
  );
}
