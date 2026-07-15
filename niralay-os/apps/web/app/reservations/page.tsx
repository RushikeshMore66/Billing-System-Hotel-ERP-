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

const reservations = [
  { id: "RES-2847", guest: "Arjun Mehta", email: "arjun@email.com", room: "Deluxe Suite 301", type: "Suite", checkIn: "14 Jul", checkOut: "16 Jul", nights: 2, guests: 2, amount: 18500, source: "Direct", status: "checked-in" },
  { id: "RES-2848", guest: "Priya Sharma", email: "priya@email.com", room: "Garden View 105", type: "Deluxe", checkIn: "14 Jul", checkOut: "17 Jul", nights: 3, guests: 1, amount: 24750, source: "Booking.com", status: "pending" },
  { id: "RES-2849", guest: "Rahul Patel", email: "rahul@email.com", room: "Honeymoon Villa", type: "Villa", checkIn: "15 Jul", checkOut: "19 Jul", nights: 4, guests: 2, amount: 56000, source: "Direct", status: "confirmed" },
  { id: "RES-2850", guest: "Dr. Kavya Nair", email: "kavya@email.com", room: "Executive 208", type: "Superior", checkIn: "15 Jul", checkOut: "16 Jul", nights: 1, guests: 1, amount: 8200, source: "Agoda", status: "confirmed" },
  { id: "RES-2846", guest: "Vikram Desai", email: "vikram@email.com", room: "Superior 412", type: "Superior", checkIn: "12 Jul", checkOut: "14 Jul", nights: 2, guests: 2, amount: 14400, source: "Direct", status: "checkout" },
  { id: "RES-2845", guest: "Meera Joshi", email: "meera@email.com", room: "Pool View 220", type: "Deluxe", checkIn: "11 Jul", checkOut: "13 Jul", nights: 2, guests: 1, amount: 16000, source: "MakeMyTrip", status: "checkout" },
  { id: "RES-2851", guest: "Suresh Kumar", email: "suresh@email.com", room: "Standard 304", type: "Standard", checkIn: "16 Jul", checkOut: "18 Jul", nights: 2, guests: 3, amount: 9600, source: "Booking.com", status: "confirmed" },
  { id: "RES-2852", guest: "Anita Bose", email: "anita@email.com", room: "Cottage 02", type: "Cottage", checkIn: "17 Jul", checkOut: "21 Jul", nights: 4, guests: 2, amount: 36000, source: "Direct", status: "confirmed" },
];

const statusConfig: Record<string, { label: string; className: string; icon: React.ElementType }> = {
  "checked-in": { label: "Checked In", className: "bg-success-50 text-success", icon: CheckCircle2 },
  confirmed: { label: "Confirmed", className: "bg-primary-50 text-primary", icon: CalendarCheck },
  pending: { label: "Pending", className: "bg-warning-50 text-warning", icon: Timer },
  checkout: { label: "Checked Out", className: "bg-gray-100 text-gray-500", icon: LogOut },
};

export default function ReservationsPage() {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");

  const filtered = reservations.filter((r) => {
    const matchSearch = r.guest.toLowerCase().includes(search.toLowerCase()) || r.id.toLowerCase().includes(search.toLowerCase());
    const matchStatus = statusFilter === "all" || r.status === statusFilter;
    return matchSearch && matchStatus;
  });

  const stats = {
    total: reservations.length,
    checkedIn: reservations.filter((r) => r.status === "checked-in").length,
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
            {["all", "checked-in", "confirmed", "pending", "checkout"].map((s) => (
              <button key={s} onClick={() => setStatusFilter(s)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${statusFilter === s ? "bg-primary text-white" : "bg-background text-text-secondary hover:bg-border"}`}>
                {s === "all" ? "All" : s === "checked-in" ? "In-House" : s === "checkout" ? "Checked Out" : s.charAt(0).toUpperCase() + s.slice(1)}
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
              {filtered.map((r) => {
                const cfg = statusConfig[r.status];
                return (
                  <tr key={r.id} className="cursor-pointer">
                    <td>
                      <div className="flex items-center gap-2.5">
                        <div className="flex items-center justify-center rounded-full text-xs font-bold text-white shrink-0"
                          style={{ width: 32, height: 32, background: "linear-gradient(135deg, #155E4B, #1d7a62)" }}>
                          {r.guest.charAt(0)}
                        </div>
                        <div>
                          <p className="font-semibold text-text-primary text-sm">{r.guest}</p>
                          <p className="text-xs text-text-secondary">{r.email}</p>
                        </div>
                      </div>
                    </td>
                    <td><span className="font-mono text-xs font-semibold text-text-secondary">{r.id}</span></td>
                    <td>
                      <p className="text-sm font-medium text-text-primary">{r.room}</p>
                      <p className="text-xs text-text-secondary">{r.type}</p>
                    </td>
                    <td className="text-sm text-text-primary font-medium">{r.checkIn}</td>
                    <td className="text-sm text-text-primary font-medium">{r.checkOut}</td>
                    <td className="text-sm text-text-primary">{r.nights}N</td>
                    <td><span className="ndl-badge ndl-badge-secondary text-xs">{r.source}</span></td>
                    <td className="font-semibold text-text-primary text-sm">₹{r.amount.toLocaleString("en-IN")}</td>
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
