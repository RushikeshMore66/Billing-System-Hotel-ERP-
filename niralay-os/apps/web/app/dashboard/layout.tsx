import { AppShell } from "../../shell/AppShell";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <AppShell pageTitle="Dashboard">{children}</AppShell>;
}
