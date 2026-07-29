"use client";

import { useState } from "react";
import {
  Plus,
  Search,
  Filter,
  Download,
  CheckCircle2,
  Clock,
  Timer,
  LogOut,
  CalendarCheck,
  Bed,
  ChevronUp,
  ChevronDown,
} from "lucide-react";

import { useEffect } from "react";
import { reservationApi, Reservation } from "@/services/api";
import { format } from "date-fns";

const statusConfig: Record<string, { label: string; className: string; icon: React.ElementType }> = {
  "checked_in": { label: "Checked In", className: "bg-success-50 text-success", icon: CheckCircle2 },
  confirmed: { label: "Confirmed", className: "bg-primary-50 text-primary", icon: CalendarCheck },
  pending: { label: "Pending", className: "bg-warning-50 text-warning", icon: Timer },
  "checked_out": { label: "Checked Out", className: "bg-gray-100 text-gray-500", icon: LogOut },
};

export default function ReservationsPage() {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchReservations = async () => {
      setIsLoading(true);
      try {
        const res = await reservationApi.list({ 
          search: search || undefined,
          status: statusFilter !== "all" ? statusFilter : undefined
        });
        setReservations(res.items);
      } catch (err) {
        console.error("Failed to load reservations", err);
      } finally {
        setIsLoading(false);
      }
    };
    const delayDebounceFn = setTimeout(() => {
      fetchReservations();
    }, 300);
    return () => clearTimeout(delayDebounceFn);
  }, [search, statusFilter]);

  const stats = {
    total: reservations.length,
    checkedIn: reservations.filter((r) => r.status === "checked_in").length,
    arriving: reservations.filter((r) => r.status === "confirmed").length,
    pending: reservations.filter((r) => r.status === "pending").length,
  };

  return (
    <div className="p-6 space-y-5 animate-fade-in">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="ndl-page-title">Reservations</h1>
          <p className="text-text-secondary text-sm mt-1">Manage all guest bookings and arrivals</p>
        </div>
        <button className="ndl-btn-primary gap-2">
          <Plus size={16} />
          New Reservation
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: "Total Reservations", value: stats.total, icon: CalendarCheck, color: "#49617A" },
          { label: "Currently In-House", value: stats.checkedIn, icon: CheckCircle2, color: "#155E4B" },
          { label: "Arriving Today", value: stats.arriving, icon: Bed, color: "#D4AF37" },
          { label: "Pending Confirmation", value: stats.pending, icon: Timer, color: "#DC2626" },
        ].map((s) => (
          <div key={s.label} className="ndl-card p-4 flex items-center gap-3">
            <div className="flex items-center justify-center rounded-xl" style={{ width: 40, height: 40, background: `${s.color}18` }}>
              <s.icon size={18} style={{ color: s.color }} />
            </div>
            <div>
              <p className="text-xl font-bold text-text-primary">{s.value}</p>
              <p className="text-xs text-text-secondary">{s.label}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Table Card */}
      <div className="ndl-card overflow-hidden">
        {/* Toolbar */}
        <div className="flex items-center gap-3 px-5 py-4 border-b border-border">
          <div className="relative flex-1 max-w-sm">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-secondary pointer-events-none" />
            <input type="text" placeholder="Search by guest or ID…" value={search} onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-background border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all" />
          </div>
          {/* Status Filter */}
          <div className="flex items-center gap-1.5">
            {["all", "checked_in", "confirmed", "pending", "checked_out"].map((s) => (
              <button key={s} onClick={() => setStatusFilter(s)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${statusFilter === s ? "bg-primary text-white" : "bg-background text-text-secondary hover:bg-border"}`}>
                {s === "all" ? "All" : s === "checked_in" ? "In-House" : s === "checked_out" ? "Checked Out" : s.charAt(0).toUpperCase() + s.slice(1)}
              </button>
            ))}
          </div>
          <button className="ndl-btn-secondary gap-2 text-xs">
            <Download size={14} /> Export
          </button>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="ndl-table">
            <thead>
              <tr>
                <th>Guest</th>
                <th>Reservation ID</th>
                <th>Room</th>
                <th>Check-in</th>
                <th>Check-out</th>
                <th>Nights</th>
                <th>Source</th>
                <th>Amount</th>
                <th>Status</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {reservations.length === 0 && !isLoading && (
                <tr>
                  <td colSpan={10} className="text-center py-8 text-text-secondary">
                    No reservations found.
                  </td>
                </tr>
              )}
              {reservations.map((r) => {
                const cfg = statusConfig[r.status] || { label: r.status, className: "bg-gray-100 text-gray-500", icon: Timer };
                return (
                  <tr key={r.id} className="cursor-pointer">
                    <td>
                      <div className="flex items-center gap-2.5">
                        <div className="flex items-center justify-center rounded-full text-xs font-bold text-white shrink-0"
                          style={{ width: 32, height: 32, background: "linear-gradient(135deg, #155E4B, #1d7a62)" }}>
                          {r.guest?.full_name ? r.guest.full_name.charAt(0) : "G"}
                        </div>
                        <div>
                          <p className="font-semibold text-text-primary text-sm">{r.guest?.full_name || "Unknown Guest"}</p>
                          <p className="text-xs text-text-secondary">{r.guest?.email || r.guest?.phone || ""}</p>
                        </div>
                      </div>
                    </td>
                    <td><span className="font-mono text-xs font-semibold text-text-secondary">{r.reservation_number}</span></td>
                    <td>
                      <p className="text-sm font-medium text-text-primary">{r.room_id ? `Room ${r.room_id}` : "Unassigned"}</p>
                      <p className="text-xs text-text-secondary">Type: {r.room_type_id}</p>
                    </td>
                    <td className="text-sm text-text-primary font-medium">{format(new Date(r.check_in_date), "dd MMM")}</td>
                    <td className="text-sm text-text-primary font-medium">{format(new Date(r.check_out_date), "dd MMM")}</td>
                    <td className="text-sm text-text-primary">{r.nights}N</td>
                    <td><span className="ndl-badge ndl-badge-secondary text-xs uppercase">{r.source.replace("_", " ")}</span></td>
                    <td className="font-semibold text-text-primary text-sm">₹{Number(r.total_amount).toLocaleString("en-IN")}</td>
                    <td>
                      <span className={`ndl-badge text-xs ${cfg.className}`}>
                        <cfg.icon size={11} />
                        {cfg.label}
                      </span>
                    </td>
                    <td>
                      <button className="text-xs text-primary font-semibold hover:underline">View</button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-between px-5 py-3 border-t border-border">
          <p className="text-sm text-text-secondary">Showing {filtered.length} of {reservations.length} reservations</p>
          <div className="flex items-center gap-1">
            {[1, 2, 3].map((p) => (
              <button key={p} className={`w-8 h-8 rounded-lg text-sm font-medium transition-colors ${p === 1 ? "bg-primary text-white" : "text-text-secondary hover:bg-background"}`}>{p}</button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
