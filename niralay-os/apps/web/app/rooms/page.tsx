"use client";

import { useState, useEffect, useCallback } from "react";
import { Search, Plus, BedDouble, RefreshCw, AlertCircle } from "lucide-react";
import { propertyApi, type Room } from "@/services/api";

const statusConfig: Record<string, { label: string; bg: string; dot: string }> = {
  available: { label: "Available", bg: "#EDF7F3", dot: "#16A34A" },
  occupied: { label: "Occupied", bg: "#EEF1F5", dot: "#49617A" },
  out_of_order: { label: "Out of Order", bg: "#FEF2F2", dot: "#DC2626" },
  maintenance: { label: "Maintenance", bg: "#FEF2F2", dot: "#DC2626" },
  cleaning: { label: "Cleaning", bg: "#FFFBEB", dot: "#F59E0B" },
};

export default function RoomsPage() {
  const [rooms, setRooms] = useState<Room[]>([]);
  const [statusSummary, setStatusSummary] = useState<Record<string, number>>({});
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [page, setPage] = useState(1);
  const pageSize = 50;

  const fetchRooms = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [roomsResult, summaryResult] = await Promise.all([
        propertyApi.listRooms({
          search: search || undefined,
          status: statusFilter !== "all" ? statusFilter : undefined,
          page,
          size: pageSize,
        }),
        propertyApi.getRoomStatusSummary(),
      ]);
      setRooms(roomsResult.items);
      setTotal(roomsResult.total);
      setStatusSummary(summaryResult.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load rooms");
    } finally {
      setLoading(false);
    }
  }, [search, statusFilter, page]);

  useEffect(() => {
    const timer = setTimeout(fetchRooms, search ? 300 : 0);
    return () => clearTimeout(timer);
  }, [fetchRooms, search]);

  const totalPages = Math.ceil(total / pageSize);

  const summaryEntries = Object.entries(statusConfig).map(([status, cfg]) => ({
    status,
    cfg,
    count: statusSummary[status] ?? 0,
  })).filter(({ count }) => count > 0 || statusFilter === status);

  return (
    <div className="p-6 space-y-5 animate-fade-in">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="ndl-page-title">Rooms</h1>
          <p className="text-text-secondary text-sm mt-1">
            Room inventory and occupancy status
            {total > 0 && (
              <span className="ml-2 text-text-tertiary">({total} total)</span>
            )}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={fetchRooms}
            className="ndl-btn-secondary gap-2"
            disabled={loading}
            title="Refresh"
          >
            <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
          </button>
          <button className="ndl-btn-primary gap-2">
            <Plus size={16} /> Add Room
          </button>
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div className="flex items-center gap-3 p-4 rounded-xl bg-red-50 border border-red-200 text-red-700">
          <AlertCircle size={16} />
          <span className="text-sm font-medium">{error}</span>
          <button onClick={fetchRooms} className="ml-auto text-xs underline">
            Retry
          </button>
        </div>
      )}

      {/* Status summary — clickable filter chips */}
      {Object.keys(statusSummary).length > 0 && (
        <div className="grid grid-cols-4 gap-4">
          {Object.entries(statusSummary).map(([status, count]) => {
            const cfg = statusConfig[status] ?? { label: status, bg: "#F5F5F5", dot: "#9CA3AF" };
            const isActive = statusFilter === status;
            return (
              <div
                key={status}
                className={`ndl-card p-4 flex items-center gap-3 cursor-pointer transition-all ${
                  isActive ? "ring-2 ring-primary/40" : ""
                }`}
                style={{ background: cfg.bg }}
                onClick={() => {
                  setStatusFilter(isActive ? "all" : status);
                  setPage(1);
                }}
              >
                <div
                  className="flex-shrink-0 rounded-full"
                  style={{ width: 12, height: 12, background: cfg.dot }}
                />
                <div>
                  <p className="text-xl font-bold text-text-primary">{count}</p>
                  <p className="text-xs text-text-secondary capitalize">
                    {cfg.label}
                  </p>
                </div>
              </div>
            );
          })}
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
            id="rooms-search"
            type="text"
            placeholder="Search rooms…"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            className="pl-9 pr-4 py-2 bg-surface border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
          />
        </div>

        {statusFilter !== "all" && (
          <button
            onClick={() => setStatusFilter("all")}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-primary text-white"
          >
            {statusConfig[statusFilter]?.label ?? statusFilter} ×
          </button>
        )}
      </div>

      {/* Loading skeleton */}
      {loading && rooms.length === 0 && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3">
          {Array.from({ length: 10 }).map((_, i) => (
            <div
              key={i}
              className="ndl-card p-4 animate-pulse"
              style={{ background: "#F3F4F6" }}
            >
              <div className="h-10 w-10 rounded-xl bg-gray-200 mb-3" />
              <div className="h-4 w-16 bg-gray-200 rounded mb-1.5" />
              <div className="h-3 w-24 bg-gray-200 rounded" />
            </div>
          ))}
        </div>
      )}

      {/* Room Cards Grid */}
      {!loading && rooms.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3">
          {rooms.map((room) => {
            const cfg =
              statusConfig[room.status] ?? {
                label: room.status,
                bg: "#F5F5F5",
                dot: "#9CA3AF",
              };
            return (
              <div
                key={room.uuid}
                id={`room-card-${room.id}`}
                className="ndl-card p-4 cursor-pointer hover:shadow-md transition-shadow"
                style={{ background: cfg.bg }}
              >
                <div className="flex items-start justify-between mb-3">
                  <div
                    className="flex items-center justify-center rounded-xl bg-white"
                    style={{
                      width: 40,
                      height: 40,
                      boxShadow: "var(--shadow-card)",
                    }}
                  >
                    <BedDouble size={18} className="text-text-secondary" />
                  </div>
                  <div className="flex items-center gap-1.5">
                    <div
                      className="rounded-full"
                      style={{ width: 8, height: 8, background: cfg.dot }}
                    />
                    <span
                      className="text-[10px] font-semibold"
                      style={{ color: cfg.dot }}
                    >
                      {cfg.label}
                    </span>
                  </div>
                </div>
                <p className="font-bold text-text-primary text-sm">
                  {room.room_number}
                </p>
                <p className="text-xs text-text-secondary mt-0.5 truncate">
                  {room.room_type?.name ?? "—"}
                </p>
                <div className="mt-2 flex items-center justify-between">
                  <span className="text-xs text-text-secondary capitalize">
                    {room.housekeeping_status.replace(/_/g, " ")}
                  </span>
                  <span className="text-xs font-semibold text-primary">
                    {room.room_type?.base_price
                      ? `₹${parseFloat(room.room_type.base_price).toLocaleString("en-IN")}`
                      : "—"}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Empty state */}
      {!loading && !error && rooms.length === 0 && (
        <div className="flex flex-col items-center justify-center py-16 text-text-secondary">
          <BedDouble size={40} className="mb-3 opacity-20" />
          <p className="text-sm font-medium">No rooms found</p>
          <p className="text-xs mt-1 opacity-60">
            {search || statusFilter !== "all"
              ? "Try adjusting your filters"
              : "Add your first room to get started"}
          </p>
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between pt-2">
          <p className="text-xs text-text-secondary">
            Showing {(page - 1) * pageSize + 1}–{Math.min(page * pageSize, total)} of {total}
          </p>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="ndl-btn-secondary text-xs px-3 py-1.5 disabled:opacity-40"
            >
              Previous
            </button>
            <span className="text-xs text-text-secondary">
              {page} / {totalPages}
            </span>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="ndl-btn-secondary text-xs px-3 py-1.5 disabled:opacity-40"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
