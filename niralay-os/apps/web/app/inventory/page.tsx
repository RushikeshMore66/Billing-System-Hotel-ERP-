"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Package,
  AlertTriangle,
  Plus,
  Search,
  RefreshCw,
  AlertCircle,
  ChevronDown,
  TrendingDown,
} from "lucide-react";
import { inventoryApi, type InventoryItem, type InventoryCategory } from "@/services/api";

const statusConfig: Record<string, { label: string; className: string }> = {
  critical: { label: "Critical", className: "ndl-badge-danger" },
  low: { label: "Low", className: "ndl-badge-warning" },
  ok: { label: "In Stock", className: "ndl-badge-success" },
};

export default function InventoryPage() {
  const [items, setItems] = useState<InventoryItem[]>([]);
  const [categories, setCategories] = useState<InventoryCategory[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [catFilter, setCatFilter] = useState<number | null>(null);
  const [stockFilter, setStockFilter] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [itemsRes, catsRes] = await Promise.all([
        inventoryApi.listItems({
          search: search || undefined,
          category_id: catFilter ?? undefined,
          stock_level: stockFilter ?? undefined,
          page,
          size: 20,
        }),
        inventoryApi.listCategories(),
      ]);
      setItems(itemsRes.items);
      setTotal(itemsRes.total);
      setCategories(catsRes.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load inventory");
    } finally {
      setLoading(false);
    }
  }, [search, catFilter, stockFilter, page]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const alertCount = items.filter((i) => i.stock_level !== "ok").length;
  const criticalCount = items.filter((i) => i.stock_level === "critical").length;

  return (
    <div className="p-6 space-y-5 animate-fade-in">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="ndl-page-title">Inventory</h1>
          <p className="text-text-secondary text-sm mt-1">
            Stock management and procurement alerts · {total} items
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={fetchData} className="ndl-btn-secondary gap-2" disabled={loading}>
            <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
            Refresh
          </button>
          <button className="ndl-btn-primary text-sm gap-2">
            <Plus size={15} /> Add Item
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="flex items-center gap-3 p-4 rounded-xl bg-red-50 border border-red-200 text-red-700">
          <AlertCircle size={16} />
          <span className="text-sm">{error}</span>
          <button onClick={fetchData} className="ml-auto text-xs underline">Retry</button>
        </div>
      )}

      {/* Stock alerts banner */}
      {!loading && alertCount > 0 && (
        <div
          className="flex items-center gap-3 p-4 rounded-xl border"
          style={{ background: "#FEF2F2", borderColor: "#FCA5A5" }}
        >
          <AlertTriangle size={18} className="text-danger shrink-0" />
          <p className="text-sm font-medium text-danger">
            <span className="font-bold">
              {criticalCount > 0 ? `${criticalCount} critical` : ""}{" "}
              {alertCount} items
            </span>{" "}
            require immediate attention — stock levels are below minimum threshold.
          </p>
          <button
            onClick={() => setStockFilter("critical")}
            className="ml-auto text-sm font-semibold text-danger hover:underline"
          >
            View Critical
          </button>
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-tertiary" />
          <input
            type="text"
            placeholder="Search items or SKU..."
            className="ndl-input pl-9 w-full"
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          />
        </div>

        {/* Category filter */}
        <select
          className="ndl-input"
          value={catFilter ?? ""}
          onChange={(e) => { setCatFilter(e.target.value ? Number(e.target.value) : null); setPage(1); }}
        >
          <option value="">All Categories</option>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>

        {/* Stock level filter */}
        <select
          className="ndl-input"
          value={stockFilter ?? ""}
          onChange={(e) => { setStockFilter(e.target.value || null); setPage(1); }}
        >
          <option value="">All Stock Levels</option>
          <option value="critical">Critical</option>
          <option value="low">Low</option>
          <option value="ok">In Stock</option>
        </select>
      </div>

      {/* Table */}
      <div className="ndl-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border bg-surface-secondary">
                <th className="text-left px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Item</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">SKU</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Category</th>
                <th className="text-right px-4 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Current</th>
                <th className="text-right px-4 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Min</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Status</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Supplier</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {loading ? (
                Array.from({ length: 6 }).map((_, i) => (
                  <tr key={i} className="animate-pulse">
                    <td className="px-5 py-4"><div className="h-4 bg-gray-100 rounded w-32" /></td>
                    <td className="px-4 py-4"><div className="h-4 bg-gray-100 rounded w-20" /></td>
                    <td className="px-4 py-4"><div className="h-4 bg-gray-100 rounded w-24" /></td>
                    <td className="px-4 py-4"><div className="h-4 bg-gray-100 rounded w-12 ml-auto" /></td>
                    <td className="px-4 py-4"><div className="h-4 bg-gray-100 rounded w-12 ml-auto" /></td>
                    <td className="px-4 py-4"><div className="h-5 bg-gray-100 rounded-full w-16" /></td>
                    <td className="px-4 py-4"><div className="h-4 bg-gray-100 rounded w-24" /></td>
                  </tr>
                ))
              ) : items.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-16 text-center">
                    <div className="flex flex-col items-center gap-3 text-text-secondary">
                      <Package size={40} className="opacity-20" />
                      <p className="font-semibold text-sm">No inventory items found</p>
                      <p className="text-xs opacity-60">
                        {search || catFilter || stockFilter
                          ? "Try adjusting your filters"
                          : "Add your first inventory item to get started"}
                      </p>
                    </div>
                  </td>
                </tr>
              ) : (
                items.map((item) => {
                  const cfg = statusConfig[item.stock_level] ?? statusConfig.ok;
                  const pct = item.minimum_stock > 0
                    ? Math.min(100, (item.current_stock / item.minimum_stock) * 100)
                    : 100;

                  return (
                    <tr key={item.id} className="hover:bg-surface-hover transition-colors">
                      <td className="px-5 py-4">
                        <div className="flex items-center gap-3">
                          <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-primary/10">
                            <Package size={14} className="text-primary" />
                          </div>
                          <div>
                            <p className="text-sm font-semibold text-text-primary">{item.name}</p>
                            <p className="text-xs text-text-tertiary">{item.unit}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-4">
                        <span className="text-xs font-mono text-text-secondary">{item.sku}</span>
                      </td>
                      <td className="px-4 py-4">
                        <span className="text-sm text-text-secondary">{item.category?.name ?? "—"}</span>
                      </td>
                      <td className="px-4 py-4 text-right">
                        <div>
                          <p
                            className="text-sm font-bold"
                            style={{
                              color: item.stock_level === "critical" ? "#DC2626" : item.stock_level === "low" ? "#D97706" : "#155E4B",
                            }}
                          >
                            {Number(item.current_stock).toFixed(1)}
                          </p>
                          {/* Mini progress bar */}
                          <div className="mt-1 h-1 rounded-full bg-gray-200 w-16 ml-auto overflow-hidden">
                            <div
                              className="h-full rounded-full transition-all"
                              style={{
                                width: `${Math.min(100, pct)}%`,
                                background: item.stock_level === "critical" ? "#DC2626" : item.stock_level === "low" ? "#F59E0B" : "#16A34A",
                              }}
                            />
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-4 text-right">
                        <span className="text-sm text-text-secondary">{Number(item.minimum_stock).toFixed(1)}</span>
                      </td>
                      <td className="px-4 py-4">
                        <span className={`ndl-badge ${cfg.className}`}>{cfg.label}</span>
                      </td>
                      <td className="px-4 py-4">
                        <span className="text-xs text-text-secondary">{item.supplier_name ?? "—"}</span>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {total > 20 && (
          <div className="px-5 py-3 border-t border-border flex items-center justify-between">
            <p className="text-xs text-text-secondary">
              Showing {(page - 1) * 20 + 1}–{Math.min(page * 20, total)} of {total} items
            </p>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="ndl-btn-secondary text-xs px-3 py-1.5"
              >
                Previous
              </button>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={page * 20 >= total}
                className="ndl-btn-secondary text-xs px-3 py-1.5"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
