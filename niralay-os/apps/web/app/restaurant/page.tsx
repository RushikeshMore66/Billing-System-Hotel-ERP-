"use client";

import { UtensilsCrossed, Users, Clock, CheckCircle2, Plus, TrendingUp } from "lucide-react";

const tables = [
  { id: "T-1", name: "Table 1", capacity: 4, status: "occupied", order: "Butter Chicken, Dal Makhani, 2x Naan", amount: 820, time: "45 min", waiter: "Ramesh" },
  { id: "T-2", name: "Table 2", capacity: 2, status: "available", order: null, amount: 0, time: null, waiter: null },
  { id: "T-3", name: "Table 3", capacity: 6, status: "occupied", order: "Chicken Biryani, Paneer Tikka, Lassi", amount: 1240, time: "20 min", waiter: "Sunil" },
  { id: "T-4", name: "Table 4", capacity: 4, status: "billing", order: "Lamb Rogan Josh, Veg Biryani, Desserts", amount: 2150, time: "1h 10min", waiter: "Ramesh" },
  { id: "T-5", name: "Table 5", capacity: 8, status: "reserved", order: null, amount: 0, time: "7:30 PM", waiter: null },
  { id: "T-6", name: "Table 6", capacity: 2, status: "occupied", order: "Paneer Butter Masala, Garlic Naan", amount: 420, time: "15 min", waiter: "Sunil" },
  { id: "T-7", name: "Table 7", capacity: 4, status: "available", order: null, amount: 0, time: null, waiter: null },
  { id: "T-8", name: "Table 8", capacity: 4, status: "available", order: null, amount: 0, time: null, waiter: null },
  { id: "T-9", name: "Table 9", capacity: 6, status: "occupied", order: "Fish Amritsari, Dal Makhani, Bread Basket", amount: 980, time: "35 min", waiter: "Ramesh" },
  { id: "T-10", name: "Table 10", capacity: 4, status: "cleaning", order: null, amount: 0, time: null, waiter: null },
  { id: "T-11", name: "Table 11", capacity: 2, status: "available", order: null, amount: 0, time: null, waiter: null },
  { id: "T-12", name: "Table 12", capacity: 10, status: "occupied", order: "Group booking - Birthday party", amount: 4850, time: "1h 30min", waiter: "Sunil" },
];

const statusConfig: Record<string, { label: string; bg: string; border: string; textColor: string }> = {
  available: { label: "Available", bg: "#EDF7F3", border: "#A2DBCB", textColor: "#155E4B" },
  occupied: { label: "Occupied", bg: "#EEF1F5", border: "#ABB9CF", textColor: "#49617A" },
  billing: { label: "Billing", bg: "#FEF9EC", border: "#F5E391", textColor: "#D97706" },
  reserved: { label: "Reserved", bg: "#F5F3FF", border: "#C4B5FD", textColor: "#7C3AED" },
  cleaning: { label: "Cleaning", bg: "#FEF2F2", border: "#FCA5A5", textColor: "#DC2626" },
};

export default function RestaurantPage() {
  const stats = {
    occupied: tables.filter((t) => t.status === "occupied" || t.status === "billing").length,
    available: tables.filter((t) => t.status === "available").length,
    revenue: tables.reduce((s, t) => s + t.amount, 0),
    orders: tables.filter((t) => t.status === "occupied").length,
  };

  return (
    <div className="p-6 space-y-5 animate-fade-in">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="ndl-page-title">Restaurant</h1>
          <p className="text-text-secondary text-sm mt-1">Table management and live orders</p>
        </div>
        <button className="ndl-btn-primary gap-2"><Plus size={16} /> New Order</button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: "Tables Occupied", value: `${stats.occupied}/${tables.length}`, icon: UtensilsCrossed, color: "#155E4B" },
          { label: "Available Tables", value: stats.available, icon: CheckCircle2, color: "#16A34A" },
          { label: "Active Orders", value: stats.orders, icon: Clock, color: "#49617A" },
          { label: "Today Revenue", value: `₹${stats.revenue.toLocaleString("en-IN")}`, icon: TrendingUp, color: "#D4AF37" },
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

      {/* Table Grid */}
      <div className="ndl-card p-5">
        <h2 className="ndl-section-title mb-4">Floor Plan</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
          {tables.map((table) => {
            const cfg = statusConfig[table.status];
            return (
              <div key={table.id} className="rounded-xl p-4 border-2 cursor-pointer hover:shadow-md transition-all duration-150"
                style={{ background: cfg.bg, borderColor: cfg.border }}>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-bold text-base text-text-primary">{table.name}</span>
                  <div className="flex items-center gap-1">
                    <Users size={12} className="text-text-secondary" />
                    <span className="text-xs text-text-secondary">{table.capacity}</span>
                  </div>
                </div>
                <span className="text-xs font-semibold" style={{ color: cfg.textColor }}>{cfg.label}</span>
                {table.order && (
                  <p className="text-xs text-text-secondary mt-2 truncate">{table.order}</p>
                )}
                {table.amount > 0 && (
                  <div className="flex items-center justify-between mt-2">
                    <span className="text-xs font-bold text-text-primary">₹{table.amount.toLocaleString("en-IN")}</span>
                    {table.time && <span className="text-xs text-text-secondary">{table.time}</span>}
                  </div>
                )}
                {table.time && table.status === "reserved" && (
                  <p className="text-xs text-text-secondary mt-1">Reserved: {table.time}</p>
                )}
                {table.waiter && (
                  <p className="text-[11px] text-text-secondary mt-1">Waiter: {table.waiter}</p>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
