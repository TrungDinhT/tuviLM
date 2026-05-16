"use client";

import { useIsMobile } from "./_components/useIsMobile";
import { TopBar } from "./_components/TopBar";
import { Btn } from "./_components/Buttons";
import { HeroPitch } from "./_components/HeroPitch";
import { EntryForm } from "./_components/EntryForm";
import { MobileEntryForm } from "./_components/MobileEntryForm";

export default function Home() {
  const isMobile = useIsMobile();
  return (
    <div className="min-h-screen flex flex-col">
      {!isMobile && <TopBar rightActions={<Btn variant="ghost">Đăng nhập</Btn>} />}
      {isMobile ? (
        <MobileEntryForm />
      ) : (
        <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 items-center px-6 lg:px-20 gap-10 lg:gap-20 py-10">
          <HeroPitch />
          <EntryForm />
        </div>
      )}
    </div>
  );
}
