"use client";

import { useState } from "react";
import { Search, Plus, BedDouble, Wrench, CheckCircle2, Clock, Wifi } from "lucide-react";

const rooms = [
  { id: "101", name: "Standard Room 101", type: "Standard", floor: 1, capacity: 2, rate: 4800, status: "available", amenities: ["AC", "TV", "WiFi"] },
  { id: "102", name: "Standard Room 102", type: "Standard", floor: 1, capacity: 2, rate: 4800, status: "occupied", guest: "Rohit Singh", checkOut: "Jul 16", amenities: ["AC", "TV", "WiFi"] },
  { id: "103", name: "Standard Room 103", type: "Standard", floor: 1, capacity: 2, rate: 4800, status: "maintenance", amenities: ["AC", "TV", "WiFi"] },
  { id: "201", name: "Deluxe Room 201", type: "Deluxe", floor: 2, capacity: 2, rate: 7200, status: "available", amenities: ["AC", "TV", "WiFi", "Minibar"] },
  { id: "202", name: "Deluxe Room 202", type: "Deluxe", floor: 2, capacity: 3, rate: 7200, status: "occupied", guest: "Ananya Kapoor", checkOut: "Jul 17", amenities: ["AC", "TV", "WiFi", "Minibar"] },
  { id: "203", name: "Deluxe Room 203", type: "Deluxe", floor: 2, capacity: 2, rate: 7200, status: "cleaning", amenities: ["AC", "TV", "WiFi", "Minibar"] },
  { id: "301", name: "Deluxe Suite 301", type: "Suite", floor: 3, capacity: 2, rate: 12500, status: "occupied", guest: "Arjun Mehta", checkOut: "Jul 16", amenities: ["AC", "TV", "WiFi", "Minibar", "Jacuzzi"] },
  { id: "302", name: "Deluxe Suite 302", type: "Suite", floor: 3, capacity: 4, rate: 12500, status: "available", amenities: ["AC", "TV", "WiFi", "Minibar", "Jacuzzi"] },
  { id: "303", name: "Pool Suite 303", type: "Suite", floor: 3, capacity: 2, rate: 15000, status: "occupied", guest: "Sunita Rao", checkOut: "Jul 19", amenities: ["AC", "TV", "WiFi", "Minibar", "Pool View"] },
  { id: "401", name: "Executive Room 401", type: "Executive", floor: 4, capacity: 2, rate: 9500, status: "available", amenities: ["AC", "TV", "WiFi", "Work Desk"] },
  { id: "402", name: "Executive Room 402", type: "Executive", floor: 4, capacity: 2, rate: 9500, status: "occupied", guest: "Deepak Verma", checkOut: "Jul 15", amenities: ["AC", "TV", "WiFi", "Work Desk"] },
  { id: "V01", name: "Honeymoon Villa", type: "Villa", floor: 0, capacity: 2, rate: 25000, status: "occupied", guest: "Rahul & Sneha", checkOut: "Jul 19", amenities: ["AC", "TV", "WiFi", "Pool", "Butler"] },
  { id: "V02", name: "Family Cottage 02", type: "Cottage", floor: 0, capacity: 6, rate: 18000, status: "available", amenities: ["AC", "TV", "WiFi", "Kitchen"] },
];

const statusConfig: Record<string, { label: string; bg: string; dot: string }> = {
  available: { label: "Available", bg: "#EDF7F3", dot: "#16A34A" },
  occupied: { label: "Occupied", bg: "#EEF1F5", dot: "#49617A" },
  maintenance: { label: "Maintenance", bg: "#FEF2F2", dot: "#DC2626" },
  cleaning: { label: "Cleaning", bg: "#FFFBEB", dot: "#F59E0B" },
};

export default function RoomsPage() {
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");

  const filtered = rooms.filter((r) => {
    const matchSearch = r.name.toLowerCase().includes(search.toLowerCase()) || r.id.toLowerCase().includes(search.toLowerCase());
    const matchType = typeFilter === "all" || r.type.toLowerCase() === typeFilter;
    const matchStatus = statusFilter === "all" || r.status === statusFilter;
    return matchSearch && matchType && matchStatus;
  });

  const counts = {
    available: rooms.filter((r) => r.status === "available").length,
    occupied: rooms.filter((r) => r.status === "occupied").length,
    maintenance: rooms.filter((r) => r.status === "maintenance").length,
    cleaning: rooms.filter((r) => r.status === "cleaning").length,
  };

  return (
    <div className="p-6 space-y-5 animate-fade-in">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="ndl-page-title">Rooms</h1>
          <p className="text-text-secondary text-sm mt-1">Room inventory and occupancy status</p>
        </div>
        <button className="ndl-btn-primary gap-2"><Plus size={16} /> Add Room</button>
      </div>

      {/* Status summary */}
      <div className="grid grid-cols-4 gap-4">
        {Object.entries(counts).map(([status, count]) => {
          const cfg = statusConfig[status];
          return (
            <div key={status} className="ndl-card p-4 flex items-center gap-3 cursor-pointer" onClick={() => setStatusFilter(statusFilter === status ? "all" : status)}>
              <div className="flex items-center justify-center rounded-full" style={{ width: 12, height: 12, background: cfg.dot }} />
              <div>
                <p className="text-xl font-bold text-text-primary">{count}</p>
                <p className="text-xs text-text-secondary capitalize">{status}</p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3 flex-wrap">
        <div className="relative">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-secondary pointer-events-none" />
          <input type="text" placeholder="Search rooms…" value={search} onChange={(e) => setSearch(e.target.value)}
            className="pl-9 pr-4 py-2 bg-surface border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all" />
        </div>
        <div className="flex items-center gap-1.5">
          {["all", "standard", "deluxe", "suite", "executive", "villa", "cottage"].map((t) => (
            <button key={t} onClick={() => setTypeFilter(t)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all capitalize ${typeFilter === t ? "bg-primary text-white" : "bg-surface border border-border text-text-secondary hover:bg-background"}`}>
              {t}
            </button>
          ))}
        </div>
      </div>

      {/* Room Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3">
        {filtered.map((room) => {
          const cfg = statusConfig[room.status];
          return (
            <div key={room.id} className="ndl-card p-4 cursor-pointer" style={{ background: cfg.bg }}>
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center justify-center rounded-xl bg-white" style={{ width: 40, height: 40, boxShadow: "var(--shadow-card)" }}>
                  <BedDouble size={18} className="text-text-secondary" />
                </div>
                <div className="flex items-center gap-1.5">
                  <div className="rounded-full" style={{ width: 8, height: 8, background: cfg.dot }} />
                  <span className="text-[10px] font-semibold" style={{ color: cfg.dot }}>{cfg.label}</span>
                </div>
              </div>
              <p className="font-bold text-text-primary text-sm">{room.id}</p>
              <p className="text-xs text-text-secondary mt-0.5 truncate">{room.name.replace(room.id, "").trim()}</p>
              <div className="mt-2 flex items-center justify-between">
                <span className="text-xs text-text-secondary">{room.type}</span>
                <span className="text-xs font-semibold text-primary">₹{room.rate.toLocaleString("en-IN")}</span>
              </div>
              {room.guest && (
                <div className="mt-2 pt-2 border-t border-border/50">
                  <p className="text-xs font-medium text-text-primary truncate">{room.guest}</p>
                  <p className="text-xs text-text-secondary">Out: {room.checkOut}</p>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {filtered.length === 0 && (
        <div className="flex flex-col items-center justify-center py-16 text-text-secondary">
          <BedDouble size={40} className="mb-3 opacity-20" />
          <p className="text-sm font-medium">No rooms found</p>
        </div>
      )}
    </div>
  );
}
