"use client";

import { useState, useEffect, useCallback } from "react";
import {
  UtensilsCrossed,
  Users,
  CheckCircle2,
  Plus,
  RefreshCw,
  AlertCircle,
  Search,
} from "lucide-react";
import { restaurantApi, type RestaurantTable } from "@/services/api";

const statusConfig: Record<
  string,
  { label: string; bg: string; border: string; textColor: string }
> = {
  available: { label: "Available", bg: "#EDF7F3", border: "#A2DBCB", textColor: "#155E4B" },
  occupied: { label: "Occupied", bg: "#EEF1F5", border: "#ABB9CF", textColor: "#49617A" },
  reserved: { label: "Reserved", bg: "#F5F3FF", border: "#C4B5FD", textColor: "#7C3AED" },
  cleaning: { label: "Cleaning", bg: "#FEF2F2", border: "#FCA5A5", textColor: "#DC2626" },
  blocked: { label: "Blocked", bg: "#FEF9EC", border: "#F5E391", textColor: "#D97706" },
};

export default function RestaurantPage() {
  const [tables, setTables] = useState<RestaurantTable[]>([]);
  const [statusSummary, setStatusSummary] = useState<Record<string, number>>({});
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");

  const fetchTables = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [tablesResult, summaryResult] = await Promise.all([
        restaurantApi.listTables({
          search: search || undefined,
          status: statusFilter !== "all" ? statusFilter : undefined,
          size: 200,
        }),
        restaurantApi.getTableStatusSummary(),
      ]);
      setTables(tablesResult.items);
      setTotal(tablesResult.total);
      setStatusSummary(summaryResult.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load tables");
    } finally {
      setLoading(false);
    }
  }, [search, statusFilter]);

  useEffect(() => {
    const timer = setTimeout(fetchTables, search ? 300 : 0);
    return () => clearTimeout(timer);
  }, [fetchTables, search]);

  const occupied = statusSummary["occupied"] ?? 0;
  const available = statusSummary["available"] ?? 0;
  const totalCount = Object.values(statusSummary).reduce((a, b) => a + b, 0);

  return (
    <div className="p-6 space-y-5 animate-fade-in">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="ndl-page-title">Restaurant</h1>
          <p className="text-text-secondary text-sm mt-1">
            Table management and live orders
            {totalCount > 0 && (
              <span className="ml-2 text-text-tertiary">({totalCount} tables)</span>
            )}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={fetchTables}
            className="ndl-btn-secondary gap-2"
            disabled={loading}
            title="Refresh"
          >
            <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
          </button>
          <button className="ndl-btn-primary gap-2">
            <Plus size={16} /> New Order
          </button>
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div className="flex items-center gap-3 p-4 rounded-xl bg-red-50 border border-red-200 text-red-700">
          <AlertCircle size={16} />
          <span className="text-sm font-medium">{error}</span>
          <button onClick={fetchTables} className="ml-auto text-xs underline">
            Retry
          </button>
        </div>
      )}

      {/* Stats summary */}
      {totalCount > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            {
              label: "Tables Occupied",
              value: `${occupied}/${totalCount}`,
              icon: UtensilsCrossed,
              color: "#155E4B",
            },
            {
              label: "Available",
              value: available,
              icon: CheckCircle2,
              color: "#16A34A",
            },
            ...Object.entries(statusSummary)
              .filter(([s]) => !["occupied", "available"].includes(s))
              .map(([s, c]) => ({
                label: statusConfig[s]?.label ?? s,
                value: c,
                icon: UtensilsCrossed,
                color: statusConfig[s]?.textColor ?? "#9CA3AF",
              })),
          ]
            .slice(0, 4)
            .map((s) => (
              <div key={s.label} className="ndl-card p-4 flex items-center gap-3">
                <div
                  className="flex items-center justify-center rounded-xl"
                  style={{ width: 40, height: 40, background: `${s.color}18` }}
                >
                  <s.icon size={18} style={{ color: s.color }} />
                </div>
                <div>
                  <p className="text-xl font-bold text-text-primary">{s.value}</p>
                  <p className="text-xs text-text-secondary">{s.label}</p>
                </div>
              </div>
            ))}
        </div>
      )}

      {/* Filters */}
      <div className="flex items-center gap-3 flex-wrap">
        <div className="relative">
          <Search
            size={14}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-text-secondary pointer-events-none"
          />
          <input
            id="restaurant-search"
            type="text"
            placeholder="Search tables…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9 pr-4 py-2 bg-surface border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
          />
        </div>
        <div className="flex items-center gap-1.5">
          {["all", "available", "occupied", "reserved", "cleaning", "blocked"].map((s) => (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all capitalize ${
                statusFilter === s
                  ? "bg-primary text-white"
                  : "bg-surface border border-border text-text-secondary hover:bg-background"
              }`}
            >
              {s}
              {s !== "all" && (statusSummary[s] ?? 0) > 0 && (
                <span className="ml-1 opacity-70">({statusSummary[s]})</span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Loading skeleton */}
      {loading && tables.length === 0 && (
        <div className="ndl-card p-5">
          <div className="h-5 w-32 bg-gray-200 rounded mb-4 animate-pulse" />
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {Array.from({ length: 8 }).map((_, i) => (
              <div
                key={i}
                className="rounded-xl p-4 border-2 border-gray-200 bg-gray-50 animate-pulse h-24"
              />
            ))}
          </div>
        </div>
      )}

      {/* Table Grid */}
      {!loading && tables.length > 0 && (
        <div className="ndl-card p-5">
          <h2 className="ndl-section-title mb-4">
            Floor Plan
            {total > tables.length && (
              <span className="ml-2 text-xs font-normal text-text-secondary">
                (showing {tables.length} of {total})
              </span>
            )}
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {tables.map((table) => {
              const cfg =
                statusConfig[table.status] ?? {
                  label: table.status,
                  bg: "#F5F5F5",
                  border: "#E5E7EB",
                  textColor: "#6B7280",
                };
              return (
                <div
                  key={table.uuid}
                  id={`table-card-${table.id}`}
                  className="rounded-xl p-4 border-2 cursor-pointer hover:shadow-md transition-all duration-150"
                  style={{ background: cfg.bg, borderColor: cfg.border }}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-bold text-base text-text-primary">
                      {table.table_number}
                    </span>
                    <div className="flex items-center gap-1">
                      <Users size={12} className="text-text-secondary" />
                      <span className="text-xs text-text-secondary">
                        {table.capacity}
                      </span>
                    </div>
                  </div>
                  <span
                    className="text-xs font-semibold"
                    style={{ color: cfg.textColor }}
                  >
                    {cfg.label}
                  </span>
                  {table.section && (
                    <p className="text-[11px] text-text-secondary mt-1 truncate">
                      {table.section}
                    </p>
                  )}
                  <p className="text-[10px] text-text-tertiary mt-1 capitalize">
                    {table.location_type}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Empty state */}
      {!loading && !error && tables.length === 0 && (
        <div className="flex flex-col items-center justify-center py-16 text-text-secondary">
          <UtensilsCrossed size={40} className="mb-3 opacity-20" />
          <p className="text-sm font-medium">No tables found</p>
          <p className="text-xs mt-1 opacity-60">
            {search || statusFilter !== "all"
              ? "Try adjusting your filters"
              : "Add tables from the Restaurant Configuration section"}
          </p>
        </div>
      )}
    </div>
  );
}
