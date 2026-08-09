"use client";

import { useState, useEffect, useCallback } from "react";
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  BarChart3,
  Download,
  RefreshCw,
  AlertCircle,
  Plus,
  Search,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
} from "recharts";
import { dashboardApi, expenseApi, billingApi, type Expense } from "@/services/api";

function fmt(amount: number): string {
  if (amount >= 10000000) return `₹${(amount / 10000000).toFixed(1)}Cr`;
  if (amount >= 100000) return `₹${(amount / 100000).toFixed(1)}L`;
  if (amount >= 1000) return `₹${(amount / 1000).toFixed(1)}K`;
  return `₹${amount.toLocaleString("en-IN")}`;
}

const PM_LABELS: Record<string, string> = {
  cash: "Cash",
  upi: "UPI",
  credit_card: "Credit Card",
  debit_card: "Debit Card",
  bank_transfer: "Bank Transfer",
  other: "Other",
};

export default function FinancePage() {
  const [financeWidget, setFinanceWidget] = useState<any>(null);
  const [monthlyRevenue, setMonthlyRevenue] = useState<any[]>([]);
  const [cashFlow, setCashFlow] = useState<any[]>([]);
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [expenseTotal, setExpenseTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [finRes, expRes, overviewRes] = await Promise.all([
        dashboardApi.getFinanceWidget(),
        expenseApi.list({ size: 10 }),
        dashboardApi.getOverview(),
      ]);
      setFinanceWidget(finRes.data);
      setExpenses(expRes.items);
      setExpenseTotal(expRes.total);
      setCashFlow(overviewRes.data.charts.cash_flow_trend ?? []);
      setMonthlyRevenue(overviewRes.data.charts.monthly_revenue ?? []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load finance data");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const kpis = financeWidget?.kpi;
  const monthlyRev = kpis?.monthly_revenue ?? 0;
  const netProfit = kpis?.net_profit_est ?? 0;
  const pending = kpis?.pending_payments ?? 0;

  return (
    <div className="p-6 space-y-5 animate-fade-in">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="ndl-page-title">Finance</h1>
          <p className="text-text-secondary text-sm mt-1">
            Revenue, expenses and profit from real billing data
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={fetchData} className="ndl-btn-secondary gap-2" disabled={loading}>
            <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
            Refresh
          </button>
          <button className="ndl-btn-secondary gap-2 text-sm">
            <Download size={15} /> Export
          </button>
        </div>
      </div>

      {error && (
        <div className="flex items-center gap-3 p-4 rounded-xl bg-red-50 border border-red-200 text-red-700">
          <AlertCircle size={16} />
          <span className="text-sm">{error}</span>
          <button onClick={fetchData} className="ml-auto text-xs underline">Retry</button>
        </div>
      )}

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: "Monthly Revenue", value: fmt(monthlyRev), icon: TrendingUp, color: "#155E4B" },
          { label: "Net Profit (Est.)", value: fmt(netProfit), icon: DollarSign, color: "#D4AF37" },
          { label: "Pending Payments", value: fmt(pending), icon: TrendingDown, color: "#DC2626" },
          {
            label: "Profit Margin",
            value: monthlyRev > 0 ? `${((netProfit / monthlyRev) * 100).toFixed(1)}%` : "—",
            icon: BarChart3,
            color: "#49617A",
          },
        ].map((kpi) => (
          <div key={kpi.label} className="ndl-card p-5">
            {loading ? (
              <div className="animate-pulse space-y-2">
                <div className="h-4 bg-gray-100 rounded w-24" />
                <div className="h-8 bg-gray-100 rounded w-20" />
              </div>
            ) : (
              <>
                <div
                  className="flex items-center justify-center rounded-xl mb-4"
                  style={{ width: 40, height: 40, background: `${kpi.color}18` }}
                >
                  <kpi.icon size={18} style={{ color: kpi.color }} />
                </div>
                <p className="text-text-secondary text-xs font-medium mb-1">{kpi.label}</p>
                <p className="text-2xl font-bold text-text-primary">{kpi.value}</p>
              </>
            )}
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Monthly revenue */}
        <div className="ndl-card p-5">
          <div className="mb-4">
            <h3 className="font-semibold text-text-primary text-sm">Monthly Revenue</h3>
            <p className="text-xs text-text-secondary">Last 6 months (Hotel + Restaurant)</p>
          </div>
          {monthlyRevenue.some((m) => m.total > 0) ? (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={monthlyRevenue}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                <XAxis dataKey="month" tick={{ fontSize: 11 }} tickLine={false} axisLine={false} />
                <YAxis tickFormatter={(v) => fmt(v)} tick={{ fontSize: 10 }} tickLine={false} axisLine={false} />
                <Tooltip formatter={(v: number) => [fmt(v), ""]} />
                <Bar dataKey="hotel" fill="#155E4B" name="Hotel" radius={[3, 3, 0, 0]} />
                <Bar dataKey="restaurant" fill="#A7D3C5" name="Restaurant" radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex flex-col items-center justify-center h-[200px] text-text-secondary">
              <BarChart3 size={32} className="mb-2 opacity-20" />
              <p className="text-sm">No billing data yet</p>
              <p className="text-xs opacity-60 mt-1">Create bills to see revenue here</p>
            </div>
          )}
        </div>

        {/* Cash flow */}
        <div className="ndl-card p-5">
          <div className="mb-4">
            <h3 className="font-semibold text-text-primary text-sm">Cash Flow (30 days)</h3>
            <p className="text-xs text-text-secondary">Revenue vs Expenses</p>
          </div>
          {cashFlow.some((d) => d.inflow > 0 || d.outflow > 0) ? (
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={cashFlow.slice(-14)}>
                <defs>
                  <linearGradient id="inGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#155E4B" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="#155E4B" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="outGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#DC2626" stopOpacity={0.15} />
                    <stop offset="95%" stopColor="#DC2626" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                <XAxis
                  dataKey="date"
                  tickFormatter={(v) => new Date(v).toLocaleDateString("en-IN", { day: "2-digit", month: "short" })}
                  tick={{ fontSize: 10 }}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis tickFormatter={(v) => fmt(v)} tick={{ fontSize: 10 }} tickLine={false} axisLine={false} />
                <Tooltip formatter={(v: number) => [fmt(v), ""]} />
                <Area type="monotone" dataKey="inflow" stroke="#155E4B" fill="url(#inGrad)" strokeWidth={2} name="Revenue" />
                <Area type="monotone" dataKey="outflow" stroke="#DC2626" fill="url(#outGrad)" strokeWidth={1.5} strokeDasharray="4 3" name="Expenses" />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex flex-col items-center justify-center h-[200px] text-text-secondary">
              <TrendingUp size={32} className="mb-2 opacity-20" />
              <p className="text-sm">No cash flow data yet</p>
              <p className="text-xs opacity-60 mt-1">Record bills and expenses to see trends</p>
            </div>
          )}
        </div>
      </div>

      {/* Recent Expenses */}
      <div className="ndl-card overflow-hidden">
        <div className="px-5 py-4 border-b border-border flex items-center justify-between">
          <h3 className="font-semibold text-text-primary text-sm">Recent Expenses</h3>
          <div className="flex items-center gap-2">
            <span className="text-xs text-text-secondary">{expenseTotal} total</span>
            <button className="ndl-btn-primary text-xs gap-1.5 px-3 py-1.5">
              <Plus size={12} /> Add Expense
            </button>
          </div>
        </div>

        {loading ? (
          <div className="p-5 space-y-3 animate-pulse">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-12 bg-gray-50 rounded-lg" />
            ))}
          </div>
        ) : expenses.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-text-secondary">
            <DollarSign size={36} className="mb-2 opacity-20" />
            <p className="text-sm font-medium">No expenses recorded yet</p>
            <p className="text-xs mt-1 opacity-60">Add your first expense to track spending</p>
          </div>
        ) : (
          <div className="divide-y divide-border">
            {expenses.map((exp) => (
              <div key={exp.id} className="px-5 py-3 flex items-center gap-4 hover:bg-surface-hover transition-colors">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-text-primary truncate">{exp.description}</p>
                  <p className="text-xs text-text-secondary">
                    {exp.category?.name ?? "Uncategorised"} ·{" "}
                    {new Date(exp.expense_date).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" })}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-bold text-danger">−{fmt(exp.total_amount)}</p>
                  <p className="text-xs text-text-tertiary">{PM_LABELS[exp.payment_method ?? ""] ?? exp.payment_method ?? "—"}</p>
                </div>
              </div>
            ))}
          </div>
        )}

        {expenseTotal > 10 && (
          <div className="px-5 py-3 border-t border-border text-center">
            <button className="text-xs text-primary hover:underline">View all {expenseTotal} expenses →</button>
          </div>
        )}
      </div>
    </div>
  );
}
