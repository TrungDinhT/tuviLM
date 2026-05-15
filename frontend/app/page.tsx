import { TopBar } from "./_components/TopBar";
import { Btn } from "./_components/Buttons";
import { HeroPitch } from "./_components/HeroPitch";
import { EntryForm } from "./_components/EntryForm";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col">
      <TopBar rightActions={<Btn variant="ghost">Đăng nhập</Btn>} />
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 items-center px-6 lg:px-20 gap-10 lg:gap-20 py-10">
        <HeroPitch />
        <EntryForm />
      </div>
    </div>
  );
}
