import { AppShell } from "../../shell/AppShell";
export default function FinanceLayout({ children }: { children: React.ReactNode }) {
  return <AppShell pageTitle="Finance">{children}</AppShell>;
}
