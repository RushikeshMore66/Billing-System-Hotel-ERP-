"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Search,
  Plus,
  Minus,
  Trash2,
  ChevronRight,
  UtensilsCrossed,
  Printer,
  CreditCard,
  CheckCircle2,
  ClipboardList,
  XCircle,
  RefreshCw,
  AlertCircle,
  FileText,
  Receipt,
} from "lucide-react";
import { billingApi, restaurantApi, type Bill } from "@/services/api";

// ─── Types ─────────────────────────────────────────────────────

interface MenuItem {
  id: number;
  name: string;
  price: number;
  category?: string;
  is_vegetarian?: boolean;
}

interface CartItem extends MenuItem {
  qty: number;
}

// ─── Bill status config ────────────────────────────────────────

const statusConfig: Record<string, { label: string; className: string; icon: React.ElementType }> = {
  draft: { label: "Draft", className: "ndl-badge-default", icon: ClipboardList },
  issued: { label: "Issued", className: "ndl-badge-warning", icon: ClipboardList },
  paid: { label: "Paid", className: "ndl-badge-success", icon: CheckCircle2 },
  partially_paid: { label: "Partial", className: "ndl-badge-warning", icon: CheckCircle2 },
  void: { label: "Void", className: "ndl-badge-danger", icon: XCircle },
};

function fmt(amount: number): string {
  return `₹${Number(amount).toLocaleString("en-IN", { minimumFractionDigits: 2 })}`;
}

// ─── Bill list view ────────────────────────────────────────────

function BillListView({ onNewBill }: { onNewBill: () => void }) {
  const [bills, setBills] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  const fetchBills = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await billingApi.listBills({
        search: search || undefined,
        status: statusFilter || undefined,
        page,
        size: 20,
      });
      setBills(res.items);
      setTotal(res.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load bills");
    } finally {
      setLoading(false);
    }
  }, [search, statusFilter, page]);

  useEffect(() => { fetchBills(); }, [fetchBills]);

  return (
    <div className="space-y-4">
      {/* Toolbar */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-tertiary" />
          <input
            type="text"
            placeholder="Search bills..."
            className="ndl-input pl-9 w-full"
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          />
        </div>
        <select
          className="ndl-input"
          value={statusFilter}
          onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
        >
          <option value="">All Statuses</option>
          <option value="draft">Draft</option>
          <option value="issued">Issued</option>
          <option value="paid">Paid</option>
          <option value="partially_paid">Partially Paid</option>
          <option value="void">Void</option>
        </select>
        <button onClick={fetchBills} className="ndl-btn-secondary gap-2" disabled={loading}>
          <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
          Refresh
        </button>
        <button onClick={onNewBill} className="ndl-btn-primary gap-2">
          <Plus size={15} /> New Bill
        </button>
      </div>

      {error && (
        <div className="flex items-center gap-3 p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">
          <AlertCircle size={16} />
          {error}
          <button onClick={fetchBills} className="ml-auto underline text-xs">Retry</button>
        </div>
      )}

      {/* Table */}
      <div className="ndl-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border bg-surface-secondary">
                <th className="text-left px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Bill #</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Date</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Type</th>
                <th className="text-right px-4 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Total</th>
                <th className="text-right px-4 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Paid</th>
                <th className="text-right px-4 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Due</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {loading ? (
                Array.from({ length: 5 }).map((_, i) => (
                  <tr key={i} className="animate-pulse">
                    {Array.from({ length: 7 }).map((_, j) => (
                      <td key={j} className="px-4 py-4">
                        <div className="h-4 bg-gray-100 rounded w-20" />
                      </td>
                    ))}
                  </tr>
                ))
              ) : bills.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-16 text-center">
                    <div className="flex flex-col items-center gap-3 text-text-secondary">
                      <Receipt size={40} className="opacity-20" />
                      <p className="font-semibold text-sm">No bills found</p>
                      <p className="text-xs opacity-60">
                        {search || statusFilter ? "Try adjusting your filters" : "Create your first bill to get started"}
                      </p>
                      {!search && !statusFilter && (
                        <button onClick={onNewBill} className="ndl-btn-primary text-sm gap-2 mt-2">
                          <Plus size={14} /> Create First Bill
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ) : (
                bills.map((bill) => {
                  const cfg = statusConfig[bill.status] ?? statusConfig.draft;
                  const StatusIcon = cfg.icon;
                  return (
                    <tr key={bill.id} className="hover:bg-surface-hover transition-colors cursor-pointer">
                      <td className="px-5 py-4">
                        <span className="text-sm font-mono font-semibold text-primary">{bill.bill_number}</span>
                      </td>
                      <td className="px-4 py-4">
                        <span className="text-sm text-text-secondary">
                          {new Date(bill.bill_date).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" })}
                        </span>
                      </td>
                      <td className="px-4 py-4">
                        <span className="text-sm text-text-secondary capitalize">{bill.bill_type}</span>
                      </td>
                      <td className="px-4 py-4 text-right font-semibold text-sm">{fmt(bill.total_amount)}</td>
                      <td className="px-4 py-4 text-right text-sm text-success">{fmt(bill.amount_paid)}</td>
                      <td className="px-4 py-4 text-right text-sm font-bold text-danger">{fmt(bill.amount_due)}</td>
                      <td className="px-4 py-4">
                        <span className={`ndl-badge flex items-center gap-1 w-fit ${cfg.className}`}>
                          <StatusIcon size={10} />
                          {cfg.label}
                        </span>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {total > 20 && (
          <div className="px-5 py-3 border-t border-border flex items-center justify-between">
            <p className="text-xs text-text-secondary">
              Showing {(page - 1) * 20 + 1}–{Math.min(page * 20, total)} of {total} bills
            </p>
            <div className="flex gap-2">
              <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1} className="ndl-btn-secondary text-xs px-3 py-1.5">Previous</button>
              <button onClick={() => setPage((p) => p + 1)} disabled={page * 20 >= total} className="ndl-btn-secondary text-xs px-3 py-1.5">Next</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ─── New Bill / POS view ───────────────────────────────────────

function NewBillView({ onBack }: { onBack: () => void }) {
  const [menuItems, setMenuItems] = useState<MenuItem[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [cart, setCart] = useState<CartItem[]>([]);
  const [search, setSearch] = useState("");
  const [catFilter, setCatFilter] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [billType, setBillType] = useState("restaurant");
  const [tableNumber, setTableNumber] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const [itemsRes, catsRes] = await Promise.all([
          restaurantApi.listMenuItems({ size: 100 }),
          restaurantApi.listMenuCategories(),
        ]);
        setMenuItems(
          itemsRes.items.map((i: any) => ({
            id: i.id,
            name: i.name,
            price: i.price,
            category: i.category?.name,
            is_vegetarian: i.is_vegetarian,
          }))
        );
        setCategories(catsRes.data ?? []);
      } catch (err) {
        setError("Failed to load menu items");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const filtered = menuItems.filter((item) => {
    const matchSearch = item.name.toLowerCase().includes(search.toLowerCase());
    const matchCat = catFilter === null || (item as any).category_id === catFilter;
    return matchSearch && matchCat;
  });

  const addToCart = (item: MenuItem) => {
    setCart((prev) => {
      const existing = prev.find((c) => c.id === item.id);
      if (existing) return prev.map((c) => c.id === item.id ? { ...c, qty: c.qty + 1 } : c);
      return [...prev, { ...item, qty: 1 }];
    });
  };

  const removeFromCart = (id: number) => {
    setCart((prev) => {
      const existing = prev.find((c) => c.id === id);
      if (existing && existing.qty > 1) return prev.map((c) => c.id === id ? { ...c, qty: c.qty - 1 } : c);
      return prev.filter((c) => c.id !== id);
    });
  };

  const clearCart = () => setCart([]);

  const subtotal = cart.reduce((s, c) => s + c.price * c.qty, 0);
  const gst = subtotal * 0.05; // 5% GST
  const total = subtotal + gst;

  const handleCreateBill = async () => {
    if (cart.length === 0) return;
    setSubmitting(true);
    setError(null);
    try {
      const res = await billingApi.createBill({
        bill_type: billType,
        table_number: tableNumber || undefined,
        items: cart.map((c, i) => ({
          item_type: "menu_item",
          description: c.name,
          menu_item_id: c.id,
          quantity: c.qty,
          unit_price: c.price,
          tax_rate: 5, // 5% GST
          display_order: i,
        })),
      });
      setSuccess(`Bill ${res.data.bill_number} created successfully!`);
      setCart([]);
      setTimeout(() => { setSuccess(null); onBack(); }, 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create bill");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="flex gap-5 h-[calc(100vh-160px)]">
      {/* Left: Menu */}
      <div className="flex-1 flex flex-col gap-4 overflow-hidden">
        {/* Search + category filter */}
        <div className="flex items-center gap-3">
          <div className="relative flex-1">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-tertiary" />
            <input
              type="text"
              placeholder="Search menu..."
              className="ndl-input pl-9 w-full"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
        </div>

        {/* Category chips */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1">
          <button
            onClick={() => setCatFilter(null)}
            className={`shrink-0 px-3 py-1.5 rounded-full text-xs font-semibold transition-colors ${
              catFilter === null ? "bg-primary text-white" : "bg-surface-secondary text-text-secondary hover:bg-surface-hover"
            }`}
          >
            All
          </button>
          {categories.map((c) => (
            <button
              key={c.id}
              onClick={() => setCatFilter(c.id === catFilter ? null : c.id)}
              className={`shrink-0 px-3 py-1.5 rounded-full text-xs font-semibold transition-colors ${
                catFilter === c.id ? "bg-primary text-white" : "bg-surface-secondary text-text-secondary hover:bg-surface-hover"
              }`}
            >
              {c.name}
            </button>
          ))}
        </div>

        {/* Menu grid */}
        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
              {Array.from({ length: 8 }).map((_, i) => (
                <div key={i} className="ndl-card p-4 animate-pulse">
                  <div className="h-4 bg-gray-100 rounded w-24 mb-2" />
                  <div className="h-6 bg-gray-100 rounded w-16" />
                </div>
              ))}
            </div>
          ) : filtered.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 text-text-secondary">
              <UtensilsCrossed size={36} className="mb-2 opacity-20" />
              <p className="text-sm">No menu items found</p>
              <p className="text-xs opacity-60 mt-1">Add menu items in the Restaurant configuration</p>
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
              {filtered.map((item) => {
                const inCart = cart.find((c) => c.id === item.id);
                return (
                  <button
                    key={item.id}
                    onClick={() => addToCart(item)}
                    className={`ndl-card p-4 text-left transition-all hover:shadow-md hover:border-primary/30 ${
                      inCart ? "border-primary/40 bg-primary/5" : ""
                    }`}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div
                        className="w-2 h-2 rounded-full flex-shrink-0 mt-1"
                        style={{ background: item.is_vegetarian ? "#16A34A" : "#DC2626" }}
                      />
                      {inCart && (
                        <span className="text-xs font-bold text-primary bg-primary/10 rounded-full px-2 py-0.5">
                          ×{inCart.qty}
                        </span>
                      )}
                    </div>
                    <p className="text-sm font-semibold text-text-primary leading-tight mb-1">{item.name}</p>
                    <p className="text-xs text-text-secondary">{item.category ?? "—"}</p>
                    <p className="text-sm font-bold text-primary mt-2">₹{item.price}</p>
                  </button>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Right: Cart / Bill summary */}
      <div className="w-80 flex flex-col gap-4 flex-shrink-0">
        <div className="ndl-card flex flex-col h-full overflow-hidden">
          <div className="px-5 py-4 border-b border-border flex items-center justify-between">
            <h3 className="font-semibold text-text-primary text-sm">Current Bill</h3>
            {cart.length > 0 && (
              <button onClick={clearCart} className="text-xs text-danger hover:underline">Clear</button>
            )}
          </div>

          {/* Bill meta */}
          <div className="px-4 py-3 border-b border-border space-y-2">
            <select
              className="ndl-input w-full text-sm"
              value={billType}
              onChange={(e) => setBillType(e.target.value)}
            >
              <option value="restaurant">Restaurant Bill</option>
              <option value="room">Room Bill</option>
              <option value="mixed">Mixed Bill</option>
            </select>
            <input
              type="text"
              placeholder="Table number (optional)"
              className="ndl-input w-full text-sm"
              value={tableNumber}
              onChange={(e) => setTableNumber(e.target.value)}
            />
          </div>

          {/* Cart items */}
          <div className="flex-1 overflow-y-auto px-4 py-3 space-y-2">
            {cart.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-text-secondary py-8">
                <ClipboardList size={32} className="mb-2 opacity-20" />
                <p className="text-sm">No items added</p>
                <p className="text-xs opacity-60 mt-1">Click menu items to add</p>
              </div>
            ) : (
              cart.map((item) => (
                <div key={item.id} className="flex items-center gap-2 p-2 rounded-lg hover:bg-surface-hover">
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-semibold truncate">{item.name}</p>
                    <p className="text-xs text-text-secondary">₹{item.price} × {item.qty}</p>
                  </div>
                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => removeFromCart(item.id)}
                      className="w-6 h-6 rounded-full bg-surface-secondary flex items-center justify-center hover:bg-red-50"
                    >
                      <Minus size={10} className="text-text-secondary" />
                    </button>
                    <span className="text-xs font-bold w-6 text-center">{item.qty}</span>
                    <button
                      onClick={() => addToCart(item)}
                      className="w-6 h-6 rounded-full bg-surface-secondary flex items-center justify-center hover:bg-primary/10"
                    >
                      <Plus size={10} className="text-text-secondary" />
                    </button>
                    <button
                      onClick={() => setCart((prev) => prev.filter((c) => c.id !== item.id))}
                      className="w-6 h-6 rounded-full flex items-center justify-center hover:bg-red-50 ml-1"
                    >
                      <Trash2 size={10} className="text-danger" />
                    </button>
                  </div>
                  <p className="text-xs font-bold w-14 text-right">₹{(item.price * item.qty).toLocaleString("en-IN")}</p>
                </div>
              ))
            )}
          </div>

          {/* Totals */}
          <div className="px-4 py-4 border-t border-border space-y-1.5">
            <div className="flex justify-between text-xs text-text-secondary">
              <span>Subtotal</span><span>₹{subtotal.toLocaleString("en-IN")}</span>
            </div>
            <div className="flex justify-between text-xs text-text-secondary">
              <span>GST (5%)</span><span>₹{gst.toFixed(2)}</span>
            </div>
            <div className="flex justify-between font-bold text-sm pt-1 border-t border-border mt-1">
              <span>Total</span><span className="text-primary">₹{total.toFixed(2)}</span>
            </div>
          </div>

          {/* Error / Success */}
          {error && (
            <div className="mx-4 mb-2 p-2 rounded-lg bg-red-50 text-red-700 text-xs flex items-center gap-2">
              <AlertCircle size={12} /> {error}
            </div>
          )}
          {success && (
            <div className="mx-4 mb-2 p-2 rounded-lg bg-green-50 text-green-700 text-xs flex items-center gap-2">
              <CheckCircle2 size={12} /> {success}
            </div>
          )}

          {/* Actions */}
          <div className="px-4 pb-4 space-y-2">
            <button
              onClick={handleCreateBill}
              disabled={cart.length === 0 || submitting}
              className="ndl-btn-primary w-full gap-2"
            >
              {submitting ? (
                <RefreshCw size={14} className="animate-spin" />
              ) : (
                <FileText size={14} />
              )}
              {submitting ? "Creating..." : "Create Bill"}
            </button>
            <button onClick={onBack} className="ndl-btn-secondary w-full text-sm">
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Main Page ─────────────────────────────────────────────────

export default function BillingPage() {
  const [view, setView] = useState<"list" | "new">("list");

  return (
    <div className="p-6 space-y-5 animate-fade-in">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          {view === "new" && (
            <button
              onClick={() => setView("list")}
              className="ndl-btn-secondary gap-1 text-sm px-3 py-1.5"
            >
              ← Back
            </button>
          )}
          <div>
            <h1 className="ndl-page-title">
              {view === "new" ? "New Bill" : "Billing"}
            </h1>
            <p className="text-text-secondary text-sm mt-1">
              {view === "new"
                ? "Select items and create a bill"
                : "Bill management and payment tracking"}
            </p>
          </div>
        </div>
      </div>

      {view === "list" ? (
        <BillListView onNewBill={() => setView("new")} />
      ) : (
        <NewBillView onBack={() => setView("list")} />
      )}
    </div>
  );
}
