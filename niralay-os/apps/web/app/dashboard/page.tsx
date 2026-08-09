"use client";

import { useState, useEffect, useCallback } from "react";
import {
  TrendingUp,
  BedDouble,
  UtensilsCrossed,
  Users,
  ArrowUpRight,
  ArrowDownRight,
  CalendarCheck,
  AlertTriangle,
  Clock,
  CheckCircle2,
  Timer,
  RefreshCw,
  AlertCircle,
  Wallet,
  Package,
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
import { dashboardApi, type DashboardOverview } from "@/services/api";

// ─── Helpers ─────────────────────────────────────────────────

function fmt(amount: number): string {
  if (amount >= 100000)
    return `₹${(amount / 100000).toFixed(1)}L`;
  if (amount >= 1000)
    return `₹${(amount / 1000).toFixed(1)}K`;
  return `₹${amount.toLocaleString("en-IN")}`;
}

const statusConfig: Record<string, { label: string; className: string; icon: React.ElementType }> = {
  checked_in: { label: "Checked In", className: "bg-success-50 text-success", icon: CheckCircle2 },
  confirmed: { label: "Confirmed", className: "bg-primary-50 text-primary", icon: CalendarCheck },
  pending: { label: "Pending", className: "bg-warning-50 text-warning", icon: Timer },
  checked_out: { label: "Checked Out", className: "bg-gray-100 text-gray-500", icon: CheckCircle2 },
};

const levelConfig: Record<string, { label: string; dotColor: string }> = {
  critical: { label: "Critical", dotColor: "#DC2626" },
  low: { label: "Low", dotColor: "#F59E0B" },
  ok: { label: "OK", dotColor: "#16A34A" },
};

// ─── Loading Skeleton ─────────────────────────────────────────

function KPISkeleton() {
  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {Array.from({ length: 4 }).map((_, i) => (
        <div key={i} className="ndl-card p-5 animate-pulse">
          <div className="h-4 w-24 bg-gray-200 rounded mb-3" />
          <div className="h-8 w-20 bg-gray-200 rounded mb-2" />
          <div className="h-3 w-16 bg-gray-200 rounded" />
        </div>
      ))}
    </div>
  );
}

// ─── KPI Card ─────────────────────────────────────────────────

interface KPICardProps {
  label: string;
  value: string;
  change?: number;
  sub?: string;
  icon: React.ElementType;
  color: string;
}

function KPICard({ label, value, change, sub, icon: Icon, color }: KPICardProps) {
  const isPositive = (change ?? 0) >= 0;
  return (
    <div className="ndl-card p-5">
      <div className="flex items-start justify-between mb-4">
        <div
          className="flex items-center justify-center rounded-xl"
          style={{ width: 40, height: 40, background: `${color}18` }}
        >
          <Icon size={18} style={{ color }} />
        </div>
        {change !== undefined && (
          <span
            className={`flex items-center gap-1 text-xs font-semibold px-2 py-1 rounded-full ${
              isPositive ? "bg-success-50 text-success" : "bg-red-50 text-red-600"
            }`}
          >
            {isPositive ? <ArrowUpRight size={12} /> : <ArrowDownRight size={12} />}
            {Math.abs(change).toFixed(1)}%
          </span>
        )}
      </div>
      <p className="text-text-secondary text-xs font-medium mb-1">{label}</p>
      <p className="text-2xl font-bold text-text-primary">{value}</p>
      {sub && <p className="text-xs text-text-tertiary mt-1">{sub}</p>}
    </div>
  );
}

// ─── Dashboard Page ───────────────────────────────────────────

export default function DashboardPage() {
  const [data, setData] = useState<DashboardOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboard = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await dashboardApi.getOverview();
      setData(res.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboard();
  }, [fetchDashboard]);

  const kpis = data?.kpis;

  return (
    <div className="p-6 space-y-5 animate-fade-in">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="ndl-page-title">Dashboard</h1>
          <p className="text-text-secondary text-sm mt-1">
            Live overview of your property
            {data?.as_of && (
              <span className="ml-2 text-text-tertiary text-xs">
                as of {new Date(data.as_of).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })}
              </span>
            )}
          </p>
        </div>
        <button
          onClick={fetchDashboard}
          className="ndl-btn-secondary gap-2"
          disabled={loading}
          title="Refresh"
        >
          <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
          Refresh
        </button>
      </div>

      {/* Error state */}
      {error && (
        <div className="flex items-center gap-3 p-4 rounded-xl bg-red-50 border border-red-200 text-red-700">
          <AlertCircle size={16} />
          <span className="text-sm font-medium">{error}</span>
          <button onClick={fetchDashboard} className="ml-auto text-xs underline">Retry</button>
        </div>
      )}

      {/* KPI Cards */}
      {loading && !data ? (
        <KPISkeleton />
      ) : kpis ? (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <KPICard
            label="Today's Revenue"
            value={fmt(kpis.revenue.today)}
            change={kpis.revenue.change_pct}
            sub={`Yesterday: ${fmt(kpis.revenue.yesterday)}`}
            icon={TrendingUp}
            color="#155E4B"
          />
          <KPICard
            label="Occupancy"
            value={`${kpis.occupancy.occupancy_pct.toFixed(0)}%`}
            sub={`${kpis.occupancy.occupied_rooms}/${kpis.occupancy.total_rooms} rooms`}
            icon={BedDouble}
            color="#49617A"
          />
          <KPICard
            label="Reservations Today"
            value={String(kpis.reservation.today_total)}
            sub={`${kpis.reservation.today_checkins} check-ins · ${kpis.reservation.today_checkouts} check-outs`}
            icon={CalendarCheck}
            color="#D4AF37"
          />
          <KPICard
            label="Pending Payments"
            value={fmt(kpis.finance.pending_payments)}
            sub={`${kpis.finance.pending_count} outstanding bills`}
            icon={Wallet}
            color="#DC2626"
          />
        </div>
      ) : null}

      {/* Secondary KPI row */}
      {kpis && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <KPICard
            label="Restaurant Orders"
            value={String(kpis.restaurant.active_orders)}
            sub={`Revenue: ${fmt(kpis.restaurant.today_revenue)}`}
            icon={UtensilsCrossed}
            color="#7C3AED"
          />
          <KPICard
            label="Employees Active"
            value={String(kpis.employee.total_active)}
            sub={`${kpis.employee.present_today} present · ${kpis.employee.on_leave} on leave`}
            icon={Users}
            color="#0891B2"
          />
          <KPICard
            label="Inventory Alerts"
            value={String(kpis.inventory.low_stock_count + kpis.inventory.critical_count)}
            sub={`${kpis.inventory.critical_count} critical · ${kpis.inventory.low_stock_count} low`}
            icon={Package}
            color="#EA580C"
          />
          <KPICard
            label="Monthly Revenue"
            value={fmt(kpis.finance.monthly_revenue)}
            sub={`Net profit est: ${fmt(kpis.finance.net_profit_est)}`}
            icon={TrendingUp}
            color="#16A34A"
          />
        </div>
      )}

      {/* Charts row */}
      {data?.charts && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {/* Revenue trend */}
          <div className="ndl-card p-5">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="font-semibold text-text-primary text-sm">Revenue Trend</h3>
                <p className="text-xs text-text-secondary">This week vs last week</p>
              </div>
            </div>
            {data.charts.revenue_trend.length > 0 ? (
              <ResponsiveContainer width="100%" height={200}>
                <AreaChart data={data.charts.revenue_trend}>
                  <defs>
                    <linearGradient id="revGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#155E4B" stopOpacity={0.15} />
                      <stop offset="95%" stopColor="#155E4B" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                  <XAxis dataKey="day" tick={{ fontSize: 11 }} tickLine={false} axisLine={false} />
                  <YAxis tickFormatter={(v) => fmt(v)} tick={{ fontSize: 10 }} tickLine={false} axisLine={false} />
                  <Tooltip formatter={(v: number) => [fmt(v), ""]} />
                  <Area type="monotone" dataKey="revenue" stroke="#155E4B" fill="url(#revGrad)" strokeWidth={2} name="This Week" />
                  <Area type="monotone" dataKey="last_week" stroke="#ABB9CF" fill="none" strokeDasharray="4 4" strokeWidth={1.5} name="Last Week" />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-[200px] text-text-secondary text-sm opacity-50">
                No revenue data yet
              </div>
            )}
          </div>

          {/* Monthly revenue */}
          <div className="ndl-card p-5">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="font-semibold text-text-primary text-sm">Monthly Revenue</h3>
                <p className="text-xs text-text-secondary">Last 6 months</p>
              </div>
            </div>
            {data.charts.monthly_revenue.some((m) => m.total > 0) ? (
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={data.charts.monthly_revenue}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                  <XAxis dataKey="month" tick={{ fontSize: 11 }} tickLine={false} axisLine={false} />
                  <YAxis tickFormatter={(v) => fmt(v)} tick={{ fontSize: 10 }} tickLine={false} axisLine={false} />
                  <Tooltip formatter={(v: number) => [fmt(v), ""]} />
                  <Bar dataKey="hotel" fill="#155E4B" name="Hotel" radius={[3, 3, 0, 0]} />
                  <Bar dataKey="restaurant" fill="#A7D3C5" name="Restaurant" radius={[3, 3, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-[200px] text-text-secondary text-sm opacity-50">
                No billing data yet — create your first bill to see revenue here
              </div>
            )}
          </div>
        </div>
      )}

      {/* Bottom row: Reservations + Inventory alerts + Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Today's reservations */}
        <div className="lg:col-span-2 ndl-card overflow-hidden">
          <div className="px-5 py-4 border-b border-border flex items-center justify-between">
            <h3 className="font-semibold text-text-primary text-sm">Today's Reservations</h3>
            <span className="text-xs text-text-secondary">
              {data?.today_reservations?.length ?? 0} records
            </span>
          </div>
          {loading ? (
            <div className="p-5 space-y-3 animate-pulse">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="h-12 bg-gray-100 rounded-lg" />
              ))}
            </div>
          ) : data?.today_reservations?.length ? (
            <div className="divide-y divide-border">
              {data.today_reservations.map((r) => {
                const cfg = statusConfig[r.status] ?? { label: r.status, className: "bg-gray-100 text-gray-500", icon: Clock };
                const StatusIcon = cfg.icon;
                return (
                  <div key={r.id} className="px-5 py-3 flex items-center gap-4 hover:bg-surface-hover transition-colors">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-semibold text-text-primary truncate">{r.guest_name}</p>
                      <p className="text-xs text-text-secondary">{r.reservation_number} · {r.room_number ?? r.room_type ?? "—"}</p>
                    </div>
                    <div className="text-right hidden md:block">
                      <p className="text-xs text-text-secondary">{r.nights}n · {new Date(r.check_in).toLocaleDateString("en-IN", { day: "2-digit", month: "short" })}–{new Date(r.check_out).toLocaleDateString("en-IN", { day: "2-digit", month: "short" })}</p>
                      <p className="text-xs font-semibold text-primary">₹{r.amount.toLocaleString("en-IN")}</p>
                    </div>
                    <span className={`flex items-center gap-1 text-[10px] font-semibold px-2 py-1 rounded-full ${cfg.className}`}>
                      <StatusIcon size={10} />
                      {cfg.label}
                    </span>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-12 text-text-secondary">
              <CalendarCheck size={32} className="mb-2 opacity-20" />
              <p className="text-sm font-medium">No reservations today</p>
              <p className="text-xs mt-1 opacity-60">Create your first reservation to see it here</p>
            </div>
          )}
        </div>

        {/* Inventory alerts + Activity */}
        <div className="space-y-5">
          {/* Inventory alerts */}
          <div className="ndl-card overflow-hidden">
            <div className="px-5 py-4 border-b border-border flex items-center gap-2">
              <AlertTriangle size={14} className="text-warning" />
              <h3 className="font-semibold text-text-primary text-sm">Inventory Alerts</h3>
              <span className="ml-auto text-xs text-text-secondary">
                {data?.inventory_alerts?.length ?? 0} alerts
              </span>
            </div>
            {loading ? (
              <div className="p-4 space-y-2 animate-pulse">
                {Array.from({ length: 3 }).map((_, i) => (
                  <div key={i} className="h-10 bg-gray-100 rounded-lg" />
                ))}
              </div>
            ) : data?.inventory_alerts?.length ? (
              <div className="divide-y divide-border">
                {data.inventory_alerts.slice(0, 5).map((alert) => {
                  const cfg = levelConfig[alert.level] ?? { label: alert.level, dotColor: "#9CA3AF" };
                  return (
                    <div key={alert.id} className="px-4 py-3 flex items-center gap-3">
                      <div
                        className="flex-shrink-0 rounded-full"
                        style={{ width: 8, height: 8, background: cfg.dotColor }}
                      />
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-semibold text-text-primary truncate">{alert.item_name}</p>
                        <p className="text-[10px] text-text-secondary">
                          {alert.current_quantity} / {alert.minimum_quantity} {alert.unit}
                        </p>
                      </div>
                      <span
                        className="text-[10px] font-bold capitalize"
                        style={{ color: cfg.dotColor }}
                      >
                        {cfg.label}
                      </span>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-8 text-text-secondary">
                <Package size={24} className="mb-2 opacity-20" />
                <p className="text-xs">No stock alerts</p>
              </div>
            )}
          </div>

          {/* Recent activity */}
          <div className="ndl-card overflow-hidden">
            <div className="px-5 py-4 border-b border-border">
              <h3 className="font-semibold text-text-primary text-sm">Recent Activity</h3>
            </div>
            {loading ? (
              <div className="p-4 space-y-2 animate-pulse">
                {Array.from({ length: 3 }).map((_, i) => (
                  <div key={i} className="h-10 bg-gray-100 rounded-lg" />
                ))}
              </div>
            ) : data?.recent_activities?.length ? (
              <div className="divide-y divide-border">
                {data.recent_activities.slice(0, 6).map((activity) => (
                  <div key={activity.id} className="px-4 py-3 flex items-start gap-3">
                    <div className="mt-0.5 flex-shrink-0 w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center">
                      <Clock size={10} className="text-primary" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs text-text-primary truncate">{activity.description}</p>
                      <p className="text-[10px] text-text-tertiary mt-0.5">
                        {activity.actor ?? "System"} · {new Date(activity.occurred_at).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-8 text-text-secondary">
                <Clock size={24} className="mb-2 opacity-20" />
                <p className="text-xs">No recent activity</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
