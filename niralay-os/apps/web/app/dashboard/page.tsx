"use client";

import {
  TrendingUp,
  BedDouble,
  UtensilsCrossed,
  Users,
  ArrowUpRight,
  ArrowDownRight,
  CalendarCheck,
  AlertTriangle,
  Sparkles,
  Clock,
  MoreHorizontal,
  CheckCircle2,
  Circle,
  Timer,
} from "lucide-react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
} from "recharts";

// ─── Mock Data ────────────────────────────────────────────────

const revenueData = [
  { day: "Mon", revenue: 42000, lastWeek: 38000 },
  { day: "Tue", revenue: 58000, lastWeek: 45000 },
  { day: "Wed", revenue: 51000, lastWeek: 52000 },
  { day: "Thu", revenue: 67000, lastWeek: 49000 },
  { day: "Fri", revenue: 89000, lastWeek: 71000 },
  { day: "Sat", revenue: 112000, lastWeek: 95000 },
  { day: "Sun", revenue: 78000, lastWeek: 68000 },
];

const occupancyData = [
  { time: "6am", hotel: 45, restaurant: 10 },
  { time: "9am", hotel: 62, restaurant: 40 },
  { time: "12pm", hotel: 71, restaurant: 85 },
  { time: "3pm", hotel: 71, restaurant: 55 },
  { time: "6pm", hotel: 78, restaurant: 70 },
  { time: "9pm", hotel: 78, restaurant: 90 },
  { time: "12am", hotel: 75, restaurant: 30 },
];

const reservations = [
  {
    id: "RES-2847",
    guest: "Arjun Mehta",
    room: "Deluxe Suite 301",
    checkIn: "Today",
    checkOut: "Jul 16",
    nights: 2,
    amount: "₹18,500",
    status: "checked-in",
    source: "Direct",
  },
  {
    id: "RES-2848",
    guest: "Priya Sharma",
    room: "Garden View 105",
    checkIn: "Today",
    checkOut: "Jul 17",
    nights: 3,
    amount: "₹24,750",
    status: "pending",
    source: "Booking.com",
  },
  {
    id: "RES-2849",
    guest: "Rahul & Sneha Patel",
    room: "Honeymoon Villa",
    checkIn: "Jul 15",
    checkOut: "Jul 19",
    nights: 4,
    amount: "₹56,000",
    status: "confirmed",
    source: "Direct",
  },
  {
    id: "RES-2850",
    guest: "Dr. Kavya Nair",
    room: "Executive Room 208",
    checkIn: "Jul 15",
    checkOut: "Jul 16",
    nights: 1,
    amount: "₹8,200",
    status: "confirmed",
    source: "Agoda",
  },
  {
    id: "RES-2846",
    guest: "Vikram Desai",
    room: "Superior Room 412",
    checkIn: "Jul 12",
    checkOut: "Today",
    nights: 2,
    amount: "₹14,400",
    status: "checkout",
    source: "Direct",
  },
];

const inventoryAlerts = [
  { item: "Basmati Rice", current: 4, unit: "kg", min: 10, level: "critical" },
  { item: "Olive Oil (Extra Virgin)", current: 2, unit: "L", min: 5, level: "critical" },
  { item: "Cleaning Detergent", current: 8, unit: "pcs", min: 15, level: "low" },
  { item: "Mineral Water (1L)", current: 45, unit: "bottles", min: 100, level: "low" },
  { item: "Bath Towels", current: 22, unit: "pcs", min: 40, level: "low" },
];

const aiInsights = [
  {
    type: "revenue",
    message: "Weekend occupancy is 23% higher than last month. Consider a ₹800 rate increase for next Saturday.",
    impact: "high",
    icon: TrendingUp,
  },
  {
    type: "restaurant",
    message: "Butter Chicken and Paneer Tikka account for 38% of restaurant revenue. Ensure stock priority.",
    impact: "medium",
    icon: UtensilsCrossed,
  },
  {
    type: "ops",
    message: "3 rooms (201, 305, 410) have been vacant for 4+ days. Recommend targeted promotions.",
    impact: "medium",
    icon: BedDouble,
  },
];

// ─── KPI Card ─────────────────────────────────────────────────

interface KPICardProps {
  title: string;
  value: string;
  change: string;
  positive: boolean;
  icon: React.ElementType;
  color: string;
  subtitle?: string;
}

function KPICard({
  title,
  value,
  change,
  positive,
  icon: Icon,
  color,
  subtitle,
}: KPICardProps) {
  return (
    <div className="ndl-card p-5 flex flex-col gap-4">
      <div className="flex items-start justify-between">
        <div
          className="flex items-center justify-center rounded-xl"
          style={{
            width: 42,
            height: 42,
            background: color,
          }}
        >
          <Icon size={20} className="text-white" />
        </div>
        <div
          className={`flex items-center gap-1 text-sm font-medium px-2 py-1 rounded-lg ${
            positive
              ? "text-success bg-success-50"
              : "text-danger bg-danger-50"
          }`}
        >
          {positive ? (
            <ArrowUpRight size={14} />
          ) : (
            <ArrowDownRight size={14} />
          )}
          {change}
        </div>
      </div>
      <div>
        <p className="text-2xl font-bold text-text-primary tracking-tight">
          {value}
        </p>
        <p className="text-sm text-text-secondary mt-1">{title}</p>
        {subtitle && (
          <p className="text-xs text-text-secondary mt-0.5 opacity-70">
            {subtitle}
          </p>
        )}
      </div>
    </div>
  );
}

// ─── Status Badge ─────────────────────────────────────────────

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, { label: string; className: string; icon: React.ElementType }> = {
    "checked-in": {
      label: "Checked In",
      className: "ndl-badge-success",
      icon: CheckCircle2,
    },
    confirmed: {
      label: "Confirmed",
      className: "ndl-badge-primary",
      icon: Circle,
    },
    pending: {
      label: "Pending",
      className: "ndl-badge-warning",
      icon: Timer,
    },
    checkout: {
      label: "Checkout",
      className: "ndl-badge-secondary",
      icon: Clock,
    },
  };
  const cfg = map[status] ?? map["pending"];
  return (
    <span className={`ndl-badge ${cfg.className}`}>
      <cfg.icon size={11} />
      {cfg.label}
    </span>
  );
}

// ─── Custom Tooltip ───────────────────────────────────────────

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white border border-border rounded-xl shadow-lg px-4 py-3">
        <p className="text-xs font-semibold text-text-secondary mb-2">{label}</p>
        {payload.map((entry: any, i: number) => (
          <p key={i} className="text-sm font-semibold" style={{ color: entry.color }}>
            {entry.name}:{" "}
            {entry.name.toLowerCase().includes("revenue")
              ? `₹${entry.value.toLocaleString("en-IN")}`
              : `${entry.value}%`}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

// ─── Dashboard Page ───────────────────────────────────────────

export default function DashboardPage() {
  const today = new Date().toLocaleDateString("en-IN", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      {/* ── Hero Banner ── */}
      <div
        className="rounded-2xl p-8 text-white overflow-hidden relative"
        style={{
          background: "linear-gradient(135deg, #155E4B 0%, #1d7a62 50%, #1a6e58 100%)",
          boxShadow: "0 8px 32px rgba(21,94,75,0.25)",
        }}
      >
        {/* Subtle pattern overlay */}
        <div
          className="absolute inset-0 opacity-5"
          style={{
            backgroundImage: `radial-gradient(circle at 30% 50%, #ffffff 1px, transparent 1px), radial-gradient(circle at 70% 50%, #ffffff 1px, transparent 1px)`,
            backgroundSize: "30px 30px",
          }}
        />
        {/* Decorative circle */}
        <div
          className="absolute -top-16 -right-16 rounded-full opacity-10"
          style={{
            width: 240,
            height: 240,
            background: "#D4AF37",
          }}
        />
        <div
          className="absolute bottom-0 right-32 rounded-full opacity-5"
          style={{
            width: 160,
            height: 160,
            background: "#ffffff",
          }}
        />

        <div className="relative flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <span
                className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold"
                style={{ background: "rgba(212,175,55,0.25)", color: "#D4AF37" }}
              >
                <div
                  className="rounded-full animate-pulse"
                  style={{ width: 6, height: 6, background: "#D4AF37" }}
                />
                Live Operations
              </span>
            </div>
            <h1 className="text-3xl font-bold text-white tracking-tight">
              Good Evening, Rushi 👋
            </h1>
            <p className="text-white/70 mt-1.5 text-base">{today}</p>
            <p className="text-white/60 text-sm mt-1">
              Niralay Resort & Restaurant — All systems operational
            </p>
          </div>
          <div className="hidden lg:flex flex-col gap-2 text-right">
            <div
              className="flex flex-col items-end px-5 py-3 rounded-xl"
              style={{ background: "rgba(255,255,255,0.12)" }}
            >
              <p className="text-white/70 text-xs font-medium">Today&apos;s Revenue</p>
              <p className="text-2xl font-bold text-white mt-1">₹1,12,450</p>
              <p className="text-xs mt-0.5" style={{ color: "#D4AF37" }}>
                +18% vs yesterday
              </p>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="relative flex items-center gap-3 mt-6 flex-wrap">
          <button
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-150"
            style={{ background: "#D4AF37", color: "#1F2937" }}
          >
            <CalendarCheck size={15} />
            New Reservation
          </button>
          <button
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-white transition-all duration-150"
            style={{ background: "rgba(255,255,255,0.15)", border: "1px solid rgba(255,255,255,0.2)" }}
          >
            <UtensilsCrossed size={15} />
            New Order
          </button>
          <button
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-white transition-all duration-150"
            style={{ background: "rgba(255,255,255,0.15)", border: "1px solid rgba(255,255,255,0.2)" }}
          >
            <Users size={15} />
            Guest Check-in
          </button>
        </div>
      </div>

      {/* ── KPI Cards ── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 xl:grid-cols-5 gap-4">
        <KPICard
          title="Today's Revenue"
          value="₹1,12,450"
          change="+18.4%"
          positive
          icon={TrendingUp}
          color="linear-gradient(135deg, #155E4B, #1d7a62)"
          subtitle="vs ₹94,970 yesterday"
        />
        <KPICard
          title="Occupancy Rate"
          value="78%"
          change="+5%"
          positive
          icon={BedDouble}
          color="linear-gradient(135deg, #49617A, #5d7a99)"
          subtitle="23 of 30 rooms"
        />
        <KPICard
          title="Active Orders"
          value="14"
          change="+3"
          positive
          icon={UtensilsCrossed}
          color="linear-gradient(135deg, #D4AF37, #e8c549)"
          subtitle="8 dine-in · 6 room service"
        />
        <KPICard
          title="Today's Check-ins"
          value="7"
          change="-2"
          positive={false}
          icon={CalendarCheck}
          color="linear-gradient(135deg, #7C3AED, #9d5bf7)"
          subtitle="3 pending · 4 done"
        />
        <KPICard
          title="Current Guests"
          value="38"
          change="+6"
          positive
          icon={Users}
          color="linear-gradient(135deg, #0EA5E9, #38bdf8)"
          subtitle="Adults: 31 · Kids: 7"
        />
      </div>

      {/* ── Charts Row ── */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        {/* Revenue Chart */}
        <div className="ndl-card p-5 xl:col-span-2">
          <div className="flex items-start justify-between mb-5">
            <div>
              <h2 className="ndl-section-title">Revenue Trend</h2>
              <p className="text-sm text-text-secondary mt-0.5">
                This week vs last week
              </p>
            </div>
            <div className="flex items-center gap-4 text-xs text-text-secondary">
              <span className="flex items-center gap-1.5">
                <span
                  className="inline-block rounded-full"
                  style={{ width: 10, height: 10, background: "#155E4B" }}
                />
                This week
              </span>
              <span className="flex items-center gap-1.5">
                <span
                  className="inline-block rounded-full"
                  style={{ width: 10, height: 10, background: "#D4AF37" }}
                />
                Last week
              </span>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={revenueData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="revGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#155E4B" stopOpacity={0.15} />
                  <stop offset="95%" stopColor="#155E4B" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="lastGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#D4AF37" stopOpacity={0.1} />
                  <stop offset="95%" stopColor="#D4AF37" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
              <XAxis
                dataKey="day"
                tick={{ fontSize: 12, fill: "#6B7280" }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                tick={{ fontSize: 12, fill: "#6B7280" }}
                axisLine={false}
                tickLine={false}
                tickFormatter={(v) => `₹${(v / 1000).toFixed(0)}k`}
              />
              <Tooltip content={<CustomTooltip />} />
              <Area
                type="monotone"
                dataKey="lastWeek"
                name="Last Week Revenue"
                stroke="#D4AF37"
                strokeWidth={2}
                fill="url(#lastGradient)"
                strokeDasharray="4 4"
              />
              <Area
                type="monotone"
                dataKey="revenue"
                name="This Week Revenue"
                stroke="#155E4B"
                strokeWidth={2.5}
                fill="url(#revGradient)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Occupancy Chart */}
        <div className="ndl-card p-5">
          <div className="mb-5">
            <h2 className="ndl-section-title">Today&apos;s Occupancy</h2>
            <p className="text-sm text-text-secondary mt-0.5">
              Hotel & Restaurant by hour
            </p>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={occupancyData} margin={{ top: 0, right: 0, left: -28, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
              <XAxis
                dataKey="time"
                tick={{ fontSize: 11, fill: "#6B7280" }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                tick={{ fontSize: 11, fill: "#6B7280" }}
                axisLine={false}
                tickLine={false}
                tickFormatter={(v) => `${v}%`}
              />
              <Tooltip content={<CustomTooltip />} />
              <Line
                type="monotone"
                dataKey="hotel"
                name="Hotel %"
                stroke="#155E4B"
                strokeWidth={2.5}
                dot={false}
              />
              <Line
                type="monotone"
                dataKey="restaurant"
                name="Restaurant %"
                stroke="#D4AF37"
                strokeWidth={2.5}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
          <div className="flex items-center justify-center gap-5 mt-3">
            <span className="flex items-center gap-1.5 text-xs text-text-secondary">
              <span className="inline-block w-3 h-0.5 rounded" style={{ background: "#155E4B" }} />
              Hotel
            </span>
            <span className="flex items-center gap-1.5 text-xs text-text-secondary">
              <span className="inline-block w-3 h-0.5 rounded" style={{ background: "#D4AF37" }} />
              Restaurant
            </span>
          </div>
        </div>
      </div>

      {/* ── Reservations Table + Finance ── */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        {/* Reservations */}
        <div className="ndl-card xl:col-span-2 overflow-hidden">
          <div className="flex items-center justify-between px-5 py-4 border-b border-border">
            <div>
              <h2 className="ndl-section-title">Today&apos;s Reservations</h2>
              <p className="text-sm text-text-secondary mt-0.5">
                Check-ins, arrivals & departures
              </p>
            </div>
            <button className="ndl-btn-secondary text-xs px-3 py-1.5 rounded-lg">
              View All
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="ndl-table">
              <thead>
                <tr>
                  <th>Guest</th>
                  <th>Room</th>
                  <th>Check-in</th>
                  <th>Check-out</th>
                  <th>Amount</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {reservations.map((r) => (
                  <tr key={r.id} className="cursor-pointer">
                    <td>
                      <div className="flex items-center gap-2.5">
                        <div
                          className="flex items-center justify-center rounded-full text-xs font-semibold text-white shrink-0"
                          style={{
                            width: 30,
                            height: 30,
                            background: "linear-gradient(135deg, #49617A, #5d7a99)",
                          }}
                        >
                          {r.guest.charAt(0)}
                        </div>
                        <div>
                          <p className="font-medium text-text-primary text-sm leading-none">
                            {r.guest}
                          </p>
                          <p className="text-xs text-text-secondary mt-0.5">
                            {r.id} · {r.source}
                          </p>
                        </div>
                      </div>
                    </td>
                    <td className="text-sm text-text-primary">{r.room}</td>
                    <td className="text-sm text-text-primary">{r.checkIn}</td>
                    <td className="text-sm text-text-primary">
                      {r.checkOut}
                      <span className="text-text-secondary ml-1">
                        ({r.nights}N)
                      </span>
                    </td>
                    <td className="text-sm font-semibold text-text-primary">
                      {r.amount}
                    </td>
                    <td>
                      <StatusBadge status={r.status} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Finance Summary + Inventory Alerts stacked */}
        <div className="space-y-4">
          {/* Finance */}
          <div className="ndl-card p-5">
            <div className="flex items-center justify-between mb-4">
              <h2 className="ndl-section-title">Finance Summary</h2>
              <span className="ndl-badge ndl-badge-secondary text-xs">July 2025</span>
            </div>
            <div className="space-y-3">
              {[
                { label: "Total Revenue", value: "₹18,42,500", color: "#155E4B", bar: 85 },
                { label: "Room Revenue", value: "₹11,20,000", color: "#49617A", bar: 61 },
                { label: "Restaurant Revenue", value: "₹5,80,000", color: "#D4AF37", bar: 31 },
                { label: "Other Revenue", value: "₹1,42,500", color: "#7C3AED", bar: 8 },
              ].map((item) => (
                <div key={item.label}>
                  <div className="flex items-center justify-between text-sm mb-1.5">
                    <span className="text-text-secondary">{item.label}</span>
                    <span className="font-semibold text-text-primary">{item.value}</span>
                  </div>
                  <div className="h-1.5 bg-background rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-500"
                      style={{ width: `${item.bar}%`, background: item.color }}
                    />
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-4 pt-4 border-t border-border flex items-center justify-between">
              <span className="text-sm text-text-secondary">Net Profit (Est.)</span>
              <span className="text-sm font-bold text-success">₹4,21,300</span>
            </div>
          </div>

          {/* Inventory Alerts */}
          <div className="ndl-card p-5">
            <div className="flex items-center justify-between mb-4">
              <h2 className="ndl-section-title">Inventory Alerts</h2>
              <span className="ndl-badge ndl-badge-danger">{inventoryAlerts.length} items</span>
            </div>
            <div className="space-y-2.5">
              {inventoryAlerts.map((alert) => (
                <div
                  key={alert.item}
                  className="flex items-center gap-3 p-3 rounded-lg"
                  style={{ background: alert.level === "critical" ? "#FEF2F2" : "#FFFBEB" }}
                >
                  <AlertTriangle
                    size={15}
                    className={
                      alert.level === "critical" ? "text-danger shrink-0" : "text-warning shrink-0"
                    }
                  />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-text-primary truncate">
                      {alert.item}
                    </p>
                    <p className="text-xs text-text-secondary">
                      {alert.current} {alert.unit} remaining (min: {alert.min})
                    </p>
                  </div>
                  <span
                    className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
                      alert.level === "critical"
                        ? "text-danger bg-danger-100"
                        : "text-warning bg-warning-100"
                    }`}
                  >
                    {alert.level === "critical" ? "Critical" : "Low"}
                  </span>
                </div>
              ))}
            </div>
            <button className="w-full mt-3 text-sm font-medium text-primary hover:text-primary-600 transition-colors">
              View All Inventory →
            </button>
          </div>
        </div>
      </div>

      {/* ── AI Insights ── */}
      <div className="ndl-card p-5">
        <div className="flex items-center gap-2 mb-4">
          <div
            className="flex items-center justify-center rounded-lg"
            style={{ width: 32, height: 32, background: "linear-gradient(135deg, #7C3AED, #9d5bf7)" }}
          >
            <Sparkles size={16} className="text-white" />
          </div>
          <div>
            <h2 className="ndl-section-title">AI Business Insights</h2>
            <p className="text-xs text-text-secondary">
              Powered by NiralayOS Intelligence Engine
            </p>
          </div>
          <span
            className="ml-auto text-xs font-medium px-2.5 py-1 rounded-full"
            style={{ background: "#EDE9FE", color: "#7C3AED" }}
          >
            3 insights today
          </span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {aiInsights.map((insight, i) => (
            <div
              key={i}
              className="flex gap-3 p-4 rounded-xl"
              style={{
                background: i === 0 ? "#EDF7F3" : i === 1 ? "#FFFBEB" : "#EEF1F5",
                border: `1px solid ${i === 0 ? "#D0EDE5" : i === 1 ? "#FEF3C7" : "#D5DCE7"}`,
              }}
            >
              <div
                className="flex items-center justify-center rounded-lg shrink-0"
                style={{
                  width: 34,
                  height: 34,
                  background:
                    i === 0
                      ? "rgba(21,94,75,0.12)"
                      : i === 1
                      ? "rgba(212,175,55,0.15)"
                      : "rgba(73,97,122,0.12)",
                }}
              >
                <insight.icon
                  size={16}
                  style={{
                    color: i === 0 ? "#155E4B" : i === 1 ? "#D4AF37" : "#49617A",
                  }}
                />
              </div>
              <div>
                <span
                  className="text-[10px] font-semibold uppercase tracking-wide"
                  style={{
                    color: i === 0 ? "#155E4B" : i === 1 ? "#D4AF37" : "#49617A",
                  }}
                >
                  {insight.impact === "high" ? "High Impact" : "Medium Impact"}
                </span>
                <p className="text-sm text-text-primary mt-1 leading-relaxed">
                  {insight.message}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
