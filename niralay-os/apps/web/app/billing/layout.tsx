import { AppShell } from "../../shell/AppShell";

export default function BillingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <AppShell pageTitle="Billing & POS">{children}</AppShell>;
}
