"use client";

import { useState } from "react";
import { Package, AlertTriangle, Plus, Search, ArrowUpRight, Download } from "lucide-react";

const inventory = [
  { id: "INV-001", name: "Basmati Rice", category: "F&B", unit: "kg", currentStock: 4, minStock: 10, maxStock: 100, lastOrder: "Jul 8", supplier: "Agro Traders", cost: 85, status: "critical" },
  { id: "INV-002", name: "Olive Oil Extra Virgin", category: "F&B", unit: "L", currentStock: 2, minStock: 5, maxStock: 30, lastOrder: "Jul 5", supplier: "Fine Foods", cost: 620, status: "critical" },
  { id: "INV-003", name: "Chicken (Frozen)", category: "F&B", unit: "kg", currentStock: 18, minStock: 20, maxStock: 80, lastOrder: "Jul 12", supplier: "Fresh Farms", cost: 280, status: "low" },
  { id: "INV-004", name: "Mineral Water 1L", category: "F&B", unit: "bottles", currentStock: 45, minStock: 100, maxStock: 500, lastOrder: "Jul 10", supplier: "Aqua Supplies", cost: 18, status: "low" },
  { id: "INV-005", name: "Bath Towels", category: "Linen", unit: "pcs", currentStock: 22, minStock: 40, maxStock: 120, lastOrder: "Jul 1", supplier: "Textile House", cost: 450, status: "low" },
  { id: "INV-006", name: "Cleaning Detergent", category: "Housekeeping", unit: "pcs", currentStock: 8, minStock: 15, maxStock: 50, lastOrder: "Jul 3", supplier: "Clean Pro", cost: 120, status: "low" },
  { id: "INV-007", name: "Coffee Beans (Arabica)", category: "F&B", unit: "kg", currentStock: 12, minStock: 5, maxStock: 30, lastOrder: "Jul 11", supplier: "Bean Masters", cost: 950, status: "ok" },
  { id: "INV-008", name: "Bed Sheets (White)", category: "Linen", unit: "sets", currentStock: 65, minStock: 30, maxStock: 150, lastOrder: "Jun 28", supplier: "Textile House", cost: 850, status: "ok" },
  { id: "INV-009", name: "Toilet Rolls", category: "Housekeeping", unit: "packs", currentStock: 120, minStock: 50, maxStock: 300, lastOrder: "Jul 9", supplier: "Clean Pro", cost: 45, status: "ok" },
  { id: "INV-010", name: "Fresh Vegetables", category: "F&B", unit: "kg", currentStock: 35, minStock: 20, maxStock: 80, lastOrder: "Jul 14", supplier: "Farm Fresh", cost: 65, status: "ok" },
  { id: "INV-011", name: "Cooking Gas (LPG)", category: "Kitchen", unit: "cylinders", currentStock: 4, minStock: 3, maxStock: 10, lastOrder: "Jul 10", supplier: "Gas Agency", cost: 1200, status: "ok" },
  { id: "INV-012", name: "Shampoo (Amenity)", category: "Housekeeping", unit: "pcs", currentStock: 280, minStock: 100, maxStock: 600, lastOrder: "Jul 2", supplier: "Luxury Amenities", cost: 35, status: "ok" },
];

const statusConfig: Record<string, { label: string; className: string }> = {
  critical: { label: "Critical", className: "ndl-badge-danger" },
  low: { label: "Low", className: "ndl-badge-warning" },
  ok: { label: "In Stock", className: "ndl-badge-success" },
};

export default function InventoryPage() {
  const [search, setSearch] = useState("");
  const [catFilter, setCatFilter] = useState("all");

  const categories = ["all", ...Array.from(new Set(inventory.map((i) => i.category)))];
  const filtered = inventory.filter((i) => {
    const matchSearch = i.name.toLowerCase().includes(search.toLowerCase());
    const matchCat = catFilter === "all" || i.category === catFilter;
    return matchSearch && matchCat;
  });

  const alertCount = inventory.filter((i) => i.status !== "ok").length;

  return (
    <div className="p-6 space-y-5 animate-fade-in">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="ndl-page-title">Inventory</h1>
          <p className="text-text-secondary text-sm mt-1">Stock management and procurement alerts</p>
        </div>
        <div className="flex items-center gap-2">
          <button className="ndl-btn-secondary text-sm gap-2"><Download size={15} /> Export</button>
          <button className="ndl-btn-primary text-sm gap-2"><Plus size={15} /> Add Item</button>
        </div>
      </div>

      {/* Alerts */}
      {alertCount > 0 && (
        <div className="flex items-center gap-3 p-4 rounded-xl border" style={{ background: "#FEF2F2", borderColor: "#FCA5A5" }}>
          <AlertTriangle size={18} className="text-danger shrink-0" />
          <p className="text-sm font-medium text-danger">
            <span className="font-bold">{alertCount} items</span> require immediate attention — stock levels are below minimum threshold.
          </p>
          <button className="ml-auto text-sm font-semibold text-danger hover:underline">Reorder Now</button>
        </div>
      )}

      {/* Filters */}
      <div className="flex items-center gap-3 flex-wrap">
        <div className="relative">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-secondary pointer-events-none" />
          <input type="text" placeholder="Search items…" value={search} onChange={(e) => setSearch(e.target.value)}
            className="pl-9 pr-4 py-2 bg-surface border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all" />
        </div>
        <div className="flex items-center gap-1.5">
          {categories.map((c) => (
            <button key={c} onClick={() => setCatFilter(c)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${catFilter === c ? "bg-primary text-white" : "bg-surface border border-border text-text-secondary hover:bg-background"}`}>
              {c === "all" ? "All" : c}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="ndl-card overflow-hidden">
        <table className="ndl-table">
          <thead>
            <tr>
              <th>Item Name</th>
              <th>Category</th>
              <th>Current Stock</th>
              <th>Min Stock</th>
              <th>Stock Level</th>
              <th>Unit Cost</th>
              <th>Last Order</th>
              <th>Supplier</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((item) => {
              const pct = Math.min(100, (item.currentStock / item.maxStock) * 100);
              const barColor = item.status === "critical" ? "#DC2626" : item.status === "low" ? "#F59E0B" : "#155E4B";
              const cfg = statusConfig[item.status];
              return (
                <tr key={item.id}>
                  <td>
                    <div className="flex items-center gap-2.5">
                      <div className="flex items-center justify-center rounded-lg bg-background border border-border" style={{ width: 32, height: 32 }}>
                        <Package size={14} className="text-text-secondary" />
                      </div>
                      <div>
                        <p className="font-semibold text-sm text-text-primary">{item.name}</p>
                        <p className="text-xs text-text-secondary font-mono">{item.id}</p>
                      </div>
                    </div>
                  </td>
                  <td><span className="ndl-badge ndl-badge-secondary">{item.category}</span></td>
                  <td className="font-bold text-text-primary">{item.currentStock} {item.unit}</td>
                  <td className="text-sm text-text-secondary">{item.minStock} {item.unit}</td>
                  <td style={{ width: 120 }}>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-1.5 bg-background rounded-full overflow-hidden">
                        <div className="h-full rounded-full" style={{ width: `${pct}%`, background: barColor }} />
                      </div>
                      <span className="text-xs text-text-secondary w-8 text-right">{pct.toFixed(0)}%</span>
                    </div>
                  </td>
                  <td className="text-sm text-text-primary">₹{item.cost}/{item.unit}</td>
                  <td className="text-sm text-text-secondary">{item.lastOrder}</td>
                  <td className="text-sm text-text-secondary">{item.supplier}</td>
                  <td><span className={`ndl-badge text-xs ${cfg.className}`}>{cfg.label}</span></td>
                  <td>
                    <button className="text-xs text-primary font-semibold hover:underline flex items-center gap-0.5">
                      <ArrowUpRight size={12} /> Reorder
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
