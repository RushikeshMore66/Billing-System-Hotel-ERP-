"use client";

import { useState } from "react";
import {
  Search,
  Plus,
  Minus,
  Trash2,
  ChevronRight,
  Users,
  BedDouble,
  UtensilsCrossed,
  TrendingUp,
  Printer,
  CreditCard,
  CheckCircle2,
  ClipboardList,
  PauseCircle,
  XCircle,
  Tag,
  Percent,
  Phone,
  User,
  ChevronDown,
} from "lucide-react";

// ─── Mock Data ────────────────────────────────────────────────

const categories = [
  { id: "all", label: "All Items", count: 42 },
  { id: "starters", label: "Starters", count: 8 },
  { id: "main", label: "Main Course", count: 14 },
  { id: "breads", label: "Breads", count: 5 },
  { id: "rice", label: "Rice & Biryani", count: 4 },
  { id: "drinks", label: "Beverages", count: 7 },
  { id: "desserts", label: "Desserts", count: 4 },
];

const menuItems = [
  { id: 1, name: "Paneer Tikka", price: 320, category: "starters", veg: true, popular: true },
  { id: 2, name: "Chicken 65", price: 380, category: "starters", veg: false, popular: true },
  { id: 3, name: "Veg Spring Rolls", price: 240, category: "starters", veg: true, popular: false },
  { id: 4, name: "Fish Amritsari", price: 420, category: "starters", veg: false, popular: false },
  { id: 5, name: "Dal Makhani", price: 280, category: "main", veg: true, popular: true },
  { id: 6, name: "Butter Chicken", price: 420, category: "main", veg: false, popular: true },
  { id: 7, name: "Paneer Butter Masala", price: 360, category: "main", veg: true, popular: true },
  { id: 8, name: "Lamb Rogan Josh", price: 520, category: "main", veg: false, popular: false },
  { id: 9, name: "Veg Biryani", price: 340, category: "rice", veg: true, popular: false },
  { id: 10, name: "Chicken Biryani", price: 420, category: "rice", veg: false, popular: true },
  { id: 11, name: "Garlic Naan", price: 60, category: "breads", veg: true, popular: true },
  { id: 12, name: "Butter Naan", price: 50, category: "breads", veg: true, popular: true },
  { id: 13, name: "Fresh Lime Soda", price: 80, category: "drinks", veg: true, popular: false },
  { id: 14, name: "Mango Lassi", price: 120, category: "drinks", veg: true, popular: true },
  { id: 15, name: "Masala Chai", price: 60, category: "drinks", veg: true, popular: false },
  { id: 16, name: "Gulab Jamun", price: 140, category: "desserts", veg: true, popular: true },
  { id: 17, name: "Rasmalai", price: 160, category: "desserts", veg: true, popular: false },
  { id: 18, name: "Kulfi Falooda", price: 180, category: "desserts", veg: true, popular: false },
];

const paymentMethods = [
  { id: "cash", label: "Cash" },
  { id: "card", label: "Card" },
  { id: "upi", label: "UPI" },
  { id: "room", label: "Room Charge" },
];

// ─── Types ────────────────────────────────────────────────────

interface OrderItem {
  id: number;
  name: string;
  price: number;
  qty: number;
  veg: boolean;
}

// ─── Quick Stats Bar ──────────────────────────────────────────

function QuickStats() {
  return (
    <div
      className="flex items-center gap-6 px-5 py-2.5 border-b border-border bg-surface"
      style={{ borderTop: "1px solid #F3F4F6" }}
    >
      {[
        { icon: TrendingUp, label: "Today's Revenue", value: "₹1,12,450", color: "#155E4B" },
        { icon: ClipboardList, label: "Active Orders", value: "14", color: "#49617A" },
        { icon: UtensilsCrossed, label: "Tables Occupied", value: "8/12", color: "#D4AF37" },
        { icon: BedDouble, label: "Rooms Occupied", value: "23/30", color: "#7C3AED" },
        { icon: Users, label: "Current Guests", value: "38", color: "#0EA5E9" },
      ].map((stat) => (
        <div key={stat.label} className="flex items-center gap-2 shrink-0">
          <div
            className="flex items-center justify-center rounded-lg"
            style={{ width: 28, height: 28, background: `${stat.color}15` }}
          >
            <stat.icon size={14} style={{ color: stat.color }} />
          </div>
          <div>
            <p className="text-[10px] text-text-secondary font-medium leading-none">{stat.label}</p>
            <p className="text-sm font-bold text-text-primary">{stat.value}</p>
          </div>
          <div className="w-px h-8 bg-border ml-4" />
        </div>
      ))}
    </div>
  );
}

// ─── Billing Page ─────────────────────────────────────────────

export default function BillingPage() {
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [orderItems, setOrderItems] = useState<OrderItem[]>([]);
  const [customerName, setCustomerName] = useState("");
  const [customerPhone, setCustomerPhone] = useState("");
  const [tableNo, setTableNo] = useState("T-1");
  const [discount, setDiscount] = useState(0);
  const [paymentMethod, setPaymentMethod] = useState("cash");
  const [orderType, setOrderType] = useState<"dine-in" | "room-service" | "takeaway">("dine-in");

  // ── Calculations ──
  const subtotal = orderItems.reduce((sum, i) => sum + i.price * i.qty, 0);
  const discountAmt = Math.round(subtotal * (discount / 100));
  const taxableAmt = subtotal - discountAmt;
  const gst = Math.round(taxableAmt * 0.05); // 5% GST for restaurant
  const total = taxableAmt + gst;

  // ── Filtered Items ──
  const filteredItems = menuItems.filter((item) => {
    const matchCat = selectedCategory === "all" || item.category === selectedCategory;
    const matchSearch =
      searchQuery === "" ||
      item.name.toLowerCase().includes(searchQuery.toLowerCase());
    return matchCat && matchSearch;
  });

  // ── Add / Remove ──
  const addItem = (item: typeof menuItems[0]) => {
    setOrderItems((prev) => {
      const existing = prev.find((o) => o.id === item.id);
      if (existing) {
        return prev.map((o) =>
          o.id === item.id ? { ...o, qty: o.qty + 1 } : o
        );
      }
      return [
        ...prev,
        { id: item.id, name: item.name, price: item.price, qty: 1, veg: item.veg },
      ];
    });
  };

  const updateQty = (id: number, delta: number) => {
    setOrderItems((prev) =>
      prev
        .map((o) => (o.id === id ? { ...o, qty: o.qty + delta } : o))
        .filter((o) => o.qty > 0)
    );
  };

  const getQty = (id: number) => orderItems.find((o) => o.id === id)?.qty ?? 0;

  const clearOrder = () => {
    setOrderItems([]);
    setCustomerName("");
    setCustomerPhone("");
    setDiscount(0);
  };

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Quick Stats */}
      <QuickStats />

      {/* Main 3-panel layout */}
      <div className="flex flex-1 overflow-hidden">
        {/* ── LEFT: Categories ── */}
        <div
          className="flex flex-col shrink-0 border-r border-border bg-surface overflow-y-auto"
          style={{ width: 180 }}
        >
          <div className="px-3 py-3 border-b border-border">
            <p className="text-[11px] font-semibold uppercase tracking-widest text-text-secondary px-1">
              Categories
            </p>
          </div>
          <div className="p-2 space-y-0.5">
            {categories.map((cat) => {
              const active = selectedCategory === cat.id;
              return (
                <button
                  key={cat.id}
                  onClick={() => setSelectedCategory(cat.id)}
                  className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 text-left ${
                    active
                      ? "bg-primary-50 text-primary"
                      : "text-text-secondary hover:bg-background hover:text-text-primary"
                  }`}
                >
                  <span className="truncate">{cat.label}</span>
                  <span
                    className={`text-xs px-1.5 py-0.5 rounded-full font-semibold ${
                      active ? "bg-primary text-white" : "bg-border text-text-secondary"
                    }`}
                  >
                    {cat.count}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        {/* ── CENTER: Menu Items Grid ── */}
        <div className="flex flex-col flex-1 overflow-hidden min-w-0 bg-background">
          {/* Search */}
          <div className="px-4 py-3 bg-surface border-b border-border">
            <div className="relative">
              <Search
                size={14}
                className="absolute left-3 top-1/2 -translate-y-1/2 text-text-secondary pointer-events-none"
              />
              <input
                type="text"
                placeholder="Search menu items…"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-8 pr-4 py-2 bg-background border border-border rounded-lg text-sm text-text-primary placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all duration-200"
              />
            </div>
          </div>

          {/* Grid */}
          <div className="flex-1 overflow-y-auto p-3">
            <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-2">
              {filteredItems.map((item) => {
                const qty = getQty(item.id);
                return (
                  <button
                    key={item.id}
                    onClick={() => addItem(item)}
                    className="relative flex flex-col items-start p-3 bg-surface rounded-xl border transition-all duration-150 text-left group"
                    style={{
                      borderColor: qty > 0 ? "#155E4B" : "#E5E7EB",
                      boxShadow: qty > 0 ? "0 0 0 2px rgba(21,94,75,0.15)" : "var(--shadow-card)",
                    }}
                  >
                    {/* Veg/Non-veg indicator */}
                    <div className="flex items-center justify-between w-full mb-2">
                      <div
                        className="rounded-sm border"
                        style={{
                          width: 12,
                          height: 12,
                          borderColor: item.veg ? "#16A34A" : "#DC2626",
                        }}
                      >
                        <div
                          className="rounded-full m-auto mt-0.5"
                          style={{
                            width: 6,
                            height: 6,
                            background: item.veg ? "#16A34A" : "#DC2626",
                          }}
                        />
                      </div>
                      {item.popular && (
                        <span
                          className="text-[9px] font-bold uppercase tracking-wide px-1.5 py-0.5 rounded-full"
                          style={{ background: "#FEF3C7", color: "#D97706" }}
                        >
                          Popular
                        </span>
                      )}
                    </div>

                    <p className="text-sm font-semibold text-text-primary leading-tight">
                      {item.name}
                    </p>
                    <p className="text-base font-bold mt-1" style={{ color: "#155E4B" }}>
                      ₹{item.price}
                    </p>

                    {/* Qty badge */}
                    {qty > 0 && (
                      <div
                        className="absolute top-2 right-2 flex items-center justify-center rounded-full text-white text-xs font-bold"
                        style={{ width: 22, height: 22, background: "#155E4B" }}
                      >
                        {qty}
                      </div>
                    )}
                  </button>
                );
              })}
            </div>

            {filteredItems.length === 0 && (
              <div className="flex flex-col items-center justify-center py-16 text-text-secondary">
                <Search size={32} className="mb-3 opacity-30" />
                <p className="text-sm font-medium">No items found</p>
                <p className="text-xs mt-1">Try a different search or category</p>
              </div>
            )}
          </div>
        </div>

        {/* ── RIGHT: Order Panel ── */}
        <div
          className="flex flex-col shrink-0 bg-surface border-l border-border overflow-hidden"
          style={{ width: 340 }}
        >
          {/* Order Header */}
          <div className="px-4 py-3 border-b border-border">
            {/* Order Type Tabs */}
            <div className="flex rounded-lg bg-background p-1 gap-1 mb-3">
              {(["dine-in", "room-service", "takeaway"] as const).map((type) => (
                <button
                  key={type}
                  onClick={() => setOrderType(type)}
                  className={`flex-1 py-1.5 rounded-md text-xs font-semibold transition-all duration-150 ${
                    orderType === type
                      ? "bg-primary text-white shadow-sm"
                      : "text-text-secondary hover:text-text-primary"
                  }`}
                >
                  {type === "dine-in" ? "Dine In" : type === "room-service" ? "Room Svc" : "Takeaway"}
                </button>
              ))}
            </div>

            {/* Table/Room selector */}
            <div className="flex items-center gap-2">
              <div className="flex-1 relative">
                <select
                  value={tableNo}
                  onChange={(e) => setTableNo(e.target.value)}
                  className="w-full appearance-none pl-3 pr-8 py-2 bg-background border border-border rounded-lg text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all duration-200"
                >
                  {orderType === "dine-in"
                    ? Array.from({ length: 12 }, (_, i) => (
                        <option key={i} value={`T-${i + 1}`}>Table {i + 1}</option>
                      ))
                    : Array.from({ length: 30 }, (_, i) => (
                        <option key={i} value={`R-${i + 101}`}>Room {i + 101}</option>
                      ))}
                </select>
                <ChevronDown size={14} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-text-secondary pointer-events-none" />
              </div>
              <span className="text-xs text-text-secondary font-medium">
                {orderItems.length} item{orderItems.length !== 1 ? "s" : ""}
              </span>
            </div>
          </div>

          {/* Customer Info */}
          <div className="px-4 py-3 border-b border-border space-y-2">
            <div className="relative">
              <User size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-secondary pointer-events-none" />
              <input
                type="text"
                placeholder="Customer name"
                value={customerName}
                onChange={(e) => setCustomerName(e.target.value)}
                className="w-full pl-8 pr-3 py-2 bg-background border border-border rounded-lg text-sm text-text-primary placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all duration-200"
              />
            </div>
            <div className="relative">
              <Phone size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-secondary pointer-events-none" />
              <input
                type="text"
                placeholder="Phone number"
                value={customerPhone}
                onChange={(e) => setCustomerPhone(e.target.value)}
                className="w-full pl-8 pr-3 py-2 bg-background border border-border rounded-lg text-sm text-text-primary placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all duration-200"
              />
            </div>
          </div>

          {/* Order Items */}
          <div className="flex-1 overflow-y-auto">
            {orderItems.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-text-secondary py-8">
                <UtensilsCrossed size={32} className="mb-3 opacity-20" />
                <p className="text-sm font-medium">No items added</p>
                <p className="text-xs mt-1">Click menu items to add to order</p>
              </div>
            ) : (
              <div className="p-3 space-y-2">
                {orderItems.map((item) => (
                  <div
                    key={item.id}
                    className="flex items-center gap-2 p-2.5 rounded-xl bg-background border border-border"
                  >
                    {/* Veg indicator */}
                    <div
                      className="rounded-sm border shrink-0"
                      style={{
                        width: 10,
                        height: 10,
                        borderColor: item.veg ? "#16A34A" : "#DC2626",
                      }}
                    >
                      <div
                        className="rounded-full m-auto"
                        style={{
                          width: 5,
                          height: 5,
                          marginTop: 2,
                          background: item.veg ? "#16A34A" : "#DC2626",
                        }}
                      />
                    </div>

                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-text-primary truncate">
                        {item.name}
                      </p>
                      <p className="text-xs text-text-secondary">
                        ₹{item.price} × {item.qty} ={" "}
                        <span className="font-semibold text-text-primary">
                          ₹{item.price * item.qty}
                        </span>
                      </p>
                    </div>

                    {/* Qty controls */}
                    <div className="flex items-center gap-1 shrink-0">
                      <button
                        onClick={() => updateQty(item.id, -1)}
                        className="flex items-center justify-center rounded-md bg-surface border border-border text-text-secondary hover:text-danger hover:border-danger transition-colors"
                        style={{ width: 24, height: 24 }}
                      >
                        <Minus size={12} />
                      </button>
                      <span className="text-sm font-bold text-text-primary w-5 text-center">
                        {item.qty}
                      </span>
                      <button
                        onClick={() => updateQty(item.id, 1)}
                        className="flex items-center justify-center rounded-md bg-primary-50 border border-primary/20 text-primary hover:bg-primary hover:text-white transition-colors"
                        style={{ width: 24, height: 24 }}
                      >
                        <Plus size={12} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Bill Summary */}
          <div className="border-t border-border px-4 py-3 space-y-2">
            {/* Discount */}
            <div className="flex items-center gap-2">
              <Percent size={13} className="text-text-secondary shrink-0" />
              <span className="text-sm text-text-secondary flex-1">Discount</span>
              <div className="flex items-center gap-1">
                {[0, 5, 10, 15].map((d) => (
                  <button
                    key={d}
                    onClick={() => setDiscount(d)}
                    className={`px-2 py-0.5 rounded text-xs font-semibold transition-all ${
                      discount === d
                        ? "bg-primary text-white"
                        : "bg-background text-text-secondary hover:bg-border"
                    }`}
                  >
                    {d}%
                  </button>
                ))}
              </div>
            </div>

            {/* Payment Method */}
            <div className="flex items-center gap-2">
              <CreditCard size={13} className="text-text-secondary shrink-0" />
              <span className="text-sm text-text-secondary flex-1">Payment</span>
              <div className="flex items-center gap-1">
                {paymentMethods.map((pm) => (
                  <button
                    key={pm.id}
                    onClick={() => setPaymentMethod(pm.id)}
                    className={`px-2 py-0.5 rounded text-xs font-semibold transition-all ${
                      paymentMethod === pm.id
                        ? "bg-secondary text-white"
                        : "bg-background text-text-secondary hover:bg-border"
                    }`}
                  >
                    {pm.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Amounts */}
            <div className="pt-2 space-y-1.5">
              <div className="flex justify-between text-sm text-text-secondary">
                <span>Subtotal</span>
                <span>₹{subtotal.toLocaleString("en-IN")}</span>
              </div>
              {discount > 0 && (
                <div className="flex justify-between text-sm text-success">
                  <span>Discount ({discount}%)</span>
                  <span>-₹{discountAmt.toLocaleString("en-IN")}</span>
                </div>
              )}
              <div className="flex justify-between text-sm text-text-secondary">
                <span>GST (5%)</span>
                <span>₹{gst.toLocaleString("en-IN")}</span>
              </div>
              <div
                className="flex justify-between text-base font-bold pt-2 border-t border-border"
                style={{ color: "#155E4B" }}
              >
                <span>Total</span>
                <span>₹{total.toLocaleString("en-IN")}</span>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="px-3 pb-3 pt-2 space-y-2 border-t border-border">
            {/* Primary action */}
            <button
              className="w-full flex items-center justify-center gap-2 py-3 rounded-xl font-semibold text-white transition-all duration-150 active:scale-[0.98]"
              style={{ background: "linear-gradient(135deg, #155E4B, #1d7a62)" }}
            >
              <CheckCircle2 size={18} />
              Complete Bill — ₹{total.toLocaleString("en-IN")}
            </button>

            {/* Secondary actions row */}
            <div className="grid grid-cols-4 gap-1.5">
              <button className="flex flex-col items-center gap-1 py-2.5 rounded-xl bg-background border border-border text-text-secondary hover:bg-warning-50 hover:text-warning hover:border-warning/30 transition-all text-xs font-medium">
                <PauseCircle size={16} />
                Hold
              </button>
              <button className="flex flex-col items-center gap-1 py-2.5 rounded-xl bg-background border border-border text-text-secondary hover:bg-primary-50 hover:text-primary hover:border-primary/30 transition-all text-xs font-medium">
                <ClipboardList size={16} />
                KOT
              </button>
              <button className="flex flex-col items-center gap-1 py-2.5 rounded-xl bg-background border border-border text-text-secondary hover:bg-secondary-50 hover:text-secondary hover:border-secondary/30 transition-all text-xs font-medium">
                <Printer size={16} />
                Print
              </button>
              <button
                onClick={clearOrder}
                className="flex flex-col items-center gap-1 py-2.5 rounded-xl bg-background border border-border text-text-secondary hover:bg-danger-50 hover:text-danger hover:border-danger/30 transition-all text-xs font-medium"
              >
                <XCircle size={16} />
                Cancel
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
