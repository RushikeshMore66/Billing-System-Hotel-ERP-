import { AppShell } from "../../shell/AppShell";
export default function EmployeesLayout({ children }: { children: React.ReactNode }) {
  return <AppShell pageTitle="Employees">{children}</AppShell>;
}
