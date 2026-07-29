"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { PanelLeftClose, PanelLeft, Loader2 } from "lucide-react";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";
import { useAuth } from "@/providers/AuthProvider";

interface AppShellProps {
  children: React.ReactNode;
  pageTitle?: string;
}

export function AppShell({ children, pageTitle }: AppShellProps) {
  const [collapsed, setCollapsed] = useState(false);
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !user) {
      router.push("/login");
    }
  }, [user, isLoading, router]);

  if (isLoading || !user) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <Loader2 size={32} className="animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* ── Sidebar ── */}
      <div
        className="shrink-0 transition-all duration-200"
        style={{ width: collapsed ? 64 : 256 }}
      >
        <Sidebar collapsed={collapsed} />
      </div>

      {/* ── Main Content Area ── */}
      <div className="flex flex-col flex-1 overflow-hidden min-w-0">
        {/* ── Topbar ── */}
        <div className="flex items-center">
          {/* Collapse toggle */}
          <button
            onClick={() => setCollapsed((c) => !c)}
            className="flex items-center justify-center w-14 h-[64px] shrink-0 text-text-secondary hover:text-text-primary hover:bg-background transition-colors duration-150 border-b border-r border-border"
            title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {collapsed ? <PanelLeft size={18} /> : <PanelLeftClose size={18} />}
          </button>
          <div className="flex-1 border-b border-border">
            <Topbar title={pageTitle} />
          </div>
        </div>

        {/* ── Scrollable Page Content ── */}
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
}

export default AppShell;
