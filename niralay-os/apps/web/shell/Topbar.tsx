"use client";

import { useState, useEffect } from "react";
import {
  Search,
  Bell,
  ChevronDown,
  Command,
  Sun,
  CloudSun,
} from "lucide-react";

// ─── Live Clock ───────────────────────────────────────────────

function LiveClock() {
  const [time, setTime] = useState<string>("");
  const [date, setDate] = useState<string>("");

  useEffect(() => {
    const update = () => {
      const now = new Date();
      setTime(
        now.toLocaleTimeString("en-IN", {
          hour: "2-digit",
          minute: "2-digit",
          hour12: true,
        })
      );
      setDate(
        now.toLocaleDateString("en-IN", {
          weekday: "short",
          day: "numeric",
          month: "short",
        })
      );
    };
    update();
    const interval = setInterval(update, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex items-center gap-2 text-right">
      <div>
        <p className="text-sm font-semibold text-text-primary leading-none">
          {time}
        </p>
        <p className="text-xs text-text-secondary mt-0.5">{date}</p>
      </div>
    </div>
  );
}

// ─── Topbar ───────────────────────────────────────────────────

interface TopbarProps {
  title?: string;
  onMenuToggle?: () => void;
}

export function Topbar({ title }: TopbarProps) {
  const [notifCount] = useState(4);

  return (
    <header
      className="flex items-center justify-between px-6 bg-surface shrink-0"
      style={{
        height: "var(--topbar-height, 64px)",
        borderBottom: "1px solid var(--color-border)",
        zIndex: 10,
      }}
    >
      {/* Left — Page Title */}
      <div className="flex items-center gap-4">
        {title && (
          <h1 className="text-lg font-semibold text-text-primary">{title}</h1>
        )}
      </div>

      {/* Center — Search */}
      <div className="flex-1 max-w-md mx-8">
        <div className="relative">
          <Search
            size={15}
            className="absolute left-3.5 top-1/2 -translate-y-1/2 text-text-secondary pointer-events-none"
          />
          <input
            type="text"
            placeholder="Search reservations, guests, rooms…"
            className="w-full pl-10 pr-10 py-2 bg-background border border-border rounded-lg text-sm text-text-primary placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all duration-200"
          />
          <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-0.5 pointer-events-none">
            <kbd className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[10px] font-medium text-text-secondary bg-border/60 border border-border">
              <Command size={9} />K
            </kbd>
          </div>
        </div>
      </div>

      {/* Right — Actions */}
      <div className="flex items-center gap-3">
        {/* Weather */}
        <div className="hidden lg:flex items-center gap-1.5 text-text-secondary text-sm">
          <Sun size={16} className="text-warning" />
          <span className="font-medium">28°C</span>
          <span className="text-text-secondary/70">Mumbai</span>
        </div>

        <div className="w-px h-5 bg-border mx-1" />

        {/* Live Clock */}
        <LiveClock />

        <div className="w-px h-5 bg-border mx-1" />

        {/* Notifications */}
        <button className="relative p-2 rounded-lg text-text-secondary hover:bg-background hover:text-text-primary transition-colors duration-150">
          <Bell size={18} />
          {notifCount > 0 && (
            <span
              className="absolute top-1.5 right-1.5 flex items-center justify-center rounded-full text-white font-semibold"
              style={{
                width: 16,
                height: 16,
                fontSize: "9px",
                background: "#DC2626",
              }}
            >
              {notifCount}
            </span>
          )}
        </button>

        {/* Profile */}
        <button className="flex items-center gap-2.5 pl-3 pr-2.5 py-1.5 rounded-lg hover:bg-background transition-colors duration-150 border border-transparent hover:border-border">
          <div
            className="flex items-center justify-center rounded-full font-semibold text-xs text-white"
            style={{
              width: 30,
              height: 30,
              background: "linear-gradient(135deg, #49617A, #5d7a99)",
            }}
          >
            RK
          </div>
          <div className="hidden md:block text-left">
            <p className="text-sm font-medium text-text-primary leading-none">
              Rushi Kumar
            </p>
            <p className="text-[11px] text-text-secondary mt-0.5">Manager</p>
          </div>
          <ChevronDown size={14} className="text-text-secondary" />
        </button>
      </div>
    </header>
  );
}

export default Topbar;
