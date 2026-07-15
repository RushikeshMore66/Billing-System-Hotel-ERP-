import { AppShell } from "../../shell/AppShell";
export default function ReservationsLayout({ children }: { children: React.ReactNode }) {
  return <AppShell pageTitle="Reservations">{children}</AppShell>;
}
