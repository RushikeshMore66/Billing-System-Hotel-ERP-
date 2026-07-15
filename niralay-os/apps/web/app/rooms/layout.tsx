import { AppShell } from "../../shell/AppShell";
export default function RoomsLayout({ children }: { children: React.ReactNode }) {
  return <AppShell pageTitle="Rooms">{children}</AppShell>;
}
