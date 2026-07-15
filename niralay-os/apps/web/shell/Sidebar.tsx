"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  CalendarCheck,
  BedDouble,
  UtensilsCrossed,
  Receipt,
  Package,
  Users,
  BarChart3,
  Settings,
  HelpCircle,
  ChevronRight,
  Sparkles,
  Building2,
} from "lucide-react";

// ─── Navigation Structure ─────────────────────────────────────

const navSections = [
  {
    label: "Operations",
    items: [
      { label: "Dashboard", icon: LayoutDashboard, href: "/dashboard" },
      { label: "Reservations", icon: CalendarCheck, href: "/reservations" },
      { label: "Rooms", icon: BedDouble, href: "/rooms" },
      { label: "Restaurant", icon: UtensilsCrossed, href: "/restaurant" },
      { label: "Billing & POS", icon: Receipt, href: "/billing" },
    ],
  },
  {
    label: "Management",
    items: [
      { label: "Inventory", icon: Package, href: "/inventory" },
      { label: "Employees", icon: Users, href: "/employees" },
      { label: "Finance", icon: BarChart3, href: "/finance" },
      { label: "AI Insights", icon: Sparkles, href: "/ai-insights" },
    ],
  },
  {
    label: "System",
    items: [
      { label: "Settings", icon: Settings, href: "/settings" },
      { label: "Help & Support", icon: HelpCircle, href: "/help" },
    ],
  },
];

// ─── Component ────────────────────────────────────────────────

interface SidebarProps {
  collapsed?: boolean;
  onToggle?: () => void;
}

export function Sidebar({ collapsed = false }: SidebarProps) {
  const pathname = usePathname();

  const isActive = (href: string) => {
    if (href === "/dashboard") return pathname === "/dashboard" || pathname === "/";
    return pathname.startsWith(href);
  };

  return (
    <aside
      className="flex flex-col h-full bg-surface border-r border-border select-none"
      style={{ width: collapsed ? "64px" : "var(--sidebar-width, 256px)" }}
    >
      {/* ── Logo ── */}
      <div className="flex items-center gap-3 px-5 py-5 border-b border-border shrink-0">
        <div
          className="flex items-center justify-center rounded-xl shrink-0"
          style={{
            width: 36,
            height: 36,
            background: "linear-gradient(135deg, #155E4B 0%, #1a7a61 100%)",
            boxShadow: "0 2px 8px rgba(21,94,75,0.25)",
          }}
        >
          <Building2 size={18} className="text-white" />
        </div>
        {!collapsed && (
          <div className="overflow-hidden">
            <p className="text-sm font-bold text-text-primary leading-none tracking-tight">
              NiralayOS
            </p>
            <p className="text-[10px] text-text-secondary mt-0.5 font-medium tracking-wide uppercase">
              Hospitality Platform
            </p>
          </div>
        )}
      </div>

      {/* ── Navigation ── */}
      <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
        {navSections.map((section) => (
          <div key={section.label} className="mb-4">
            {!collapsed && (
              <p className="px-3 mb-1.5 text-[10px] font-semibold tracking-widest uppercase text-text-secondary">
                {section.label}
              </p>
            )}
            <div className="space-y-0.5">
              {section.items.map((item) => {
                const active = isActive(item.href);
                return (
                  <Link key={item.href} href={item.href} title={item.label}>
                    <div
                      className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium cursor-pointer transition-all duration-150 ${
                        active
                          ? "bg-primary-50 text-primary"
                          : "text-text-secondary hover:bg-background hover:text-text-primary"
                      }`}
                    >
                      <item.icon
                        size={18}
                        className={`shrink-0 ${active ? "text-primary" : ""}`}
                        strokeWidth={active ? 2.5 : 2}
                      />
                      {!collapsed && (
                        <span className="truncate">{item.label}</span>
                      )}
                      {!collapsed && active && (
                        <ChevronRight
                          size={14}
                          className="ml-auto text-primary opacity-60"
                        />
                      )}
                    </div>
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      {/* ── User Profile ── */}
      <div className="shrink-0 px-3 pb-4 pt-3 border-t border-border">
        <div
          className={`flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-background cursor-pointer transition-all duration-150 ${
            collapsed ? "justify-center" : ""
          }`}
        >
          {/* Avatar */}
          <div
            className="flex items-center justify-center rounded-full shrink-0 font-semibold text-sm text-white"
            style={{
              width: 34,
              height: 34,
              background: "linear-gradient(135deg, #49617A, #5d7a99)",
            }}
          >
            RK
          </div>
          {!collapsed && (
            <div className="overflow-hidden flex-1">
              <p className="text-sm font-semibold text-text-primary truncate leading-none">
                Rushi Kumar
              </p>
              <p className="text-xs text-text-secondary mt-0.5 truncate">
                Manager
              </p>
            </div>
          )}
          {!collapsed && (
            <Settings size={14} className="text-text-secondary shrink-0" />
          )}
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;
