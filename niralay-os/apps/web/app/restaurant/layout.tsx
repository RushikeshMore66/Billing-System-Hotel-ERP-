import { AppShell } from "../../shell/AppShell";
export default function RestaurantLayout({ children }: { children: React.ReactNode }) {
  return <AppShell pageTitle="Restaurant">{children}</AppShell>;
}
