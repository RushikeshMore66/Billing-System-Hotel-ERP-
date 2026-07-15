import { AppShell } from "../../shell/AppShell";
export default function InventoryLayout({ children }: { children: React.ReactNode }) {
  return <AppShell pageTitle="Inventory">{children}</AppShell>;
}
