"use client";

import { TrendingUp, TrendingDown, DollarSign, ArrowUpRight, ArrowDownRight, BarChart3, Download } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from "recharts";

const monthlyRevenue = [
  { month: "Jan", revenue: 1240000, expense: 780000 },
  { month: "Feb", revenue: 980000, expense: 650000 },
  { month: "Mar", revenue: 1450000, expense: 890000 },
  { month: "Apr", revenue: 1680000, expense: 920000 },
  { month: "May", revenue: 1920000, expense: 1050000 },
  { month: "Jun", revenue: 2150000, expense: 1120000 },
  { month: "Jul", revenue: 1842500, expense: 980000 },
];

const transactions = [
  { id: "TXN-001", description: "Room Revenue - July", type: "income", amount: 1120000, date: "Jul 14", category: "Rooms" },
  { id: "TXN-002", description: "Restaurant Revenue - July", type: "income", amount: 580000, date: "Jul 14", category: "Restaurant" },
  { id: "TXN-003", description: "Staff Salaries - July", type: "expense", amount: 420000, date: "Jul 10", category: "HR" },
  { id: "TXN-004", description: "Inventory Purchase", type: "expense", amount: 85000, date: "Jul 9", category: "Inventory" },
  { id: "TXN-005", description: "Event Revenue - Corporate", type: "income", amount: 142500, date: "Jul 8", category: "Events" },
  { id: "TXN-006", description: "Utility Bills", type: "expense", amount: 65000, date: "Jul 5", category: "Utilities" },
  { id: "TXN-007", description: "Maintenance & Repairs", type: "expense", amount: 38000, date: "Jul 3", category: "Maintenance" },
  { id: "TXN-008", description: "Minibar Revenue", type: "income", amount: 28000, date: "Jul 2", category: "Rooms" },
];

export default function FinancePage() {
  const totalRevenue = monthlyRevenue[monthlyRevenue.length - 1].revenue;
  const totalExpense = monthlyRevenue[monthlyRevenue.length - 1].expense;
  const netProfit = totalRevenue - totalExpense;
  const profitMargin = ((netProfit / totalRevenue) * 100).toFixed(1);

  return (
    <div className="p-6 space-y-5 animate-fade-in">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="ndl-page-title">Finance</h1>
          <p className="text-text-secondary text-sm mt-1">Revenue, expenses and profit overview — July 2025</p>
        </div>
        <button className="ndl-btn-secondary gap-2 text-sm"><Download size={15} /> Export Report</button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: "Total Revenue", value: `₹${(totalRevenue / 100000).toFixed(1)}L`, change: "+18.4%", positive: true, icon: TrendingUp, color: "#155E4B" },
          { label: "Total Expenses", value: `₹${(totalExpense / 100000).toFixed(1)}L`, change: "-3.2%", positive: true, icon: TrendingDown, color: "#49617A" },
          { label: "Net Profit", value: `₹${(netProfit / 100000).toFixed(1)}L`, change: "+24.1%", positive: true, icon: DollarSign, color: "#D4AF37" },
          { label: "Profit Margin", value: `${profitMargin}%`, change: "+2.3%", positive: true, icon: BarChart3, color: "#16A34A" },
        ].map((kpi) => (
          <div key={kpi.label} className="ndl-card p-5">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center justify-center rounded-xl" style={{ width: 40, height: 40, background: `${kpi.color}18` }}>
                <kpi.icon size={18} style={{ color: kpi.color }} />
              </div>
              <span className={`flex items-center gap-0.5 text-xs font-semibold px-2 py-1 rounded-lg ${kpi.positive ? "text-success bg-success-50" : "text-danger bg-danger-50"}`}>
                {kpi.positive ? <ArrowUpRight size={12} /> : <ArrowDownRight size={12} />}{kpi.change}
              </span>
            </div>
            <p className="text-2xl font-bold text-text-primary">{kpi.value}</p>
            <p className="text-sm text-text-secondary mt-1">{kpi.label}</p>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <div className="ndl-card p-5">
          <h2 className="ndl-section-title mb-1">Revenue vs Expenses</h2>
          <p className="text-sm text-text-secondary mb-5">January — July 2025</p>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={monthlyRevenue} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
              <XAxis dataKey="month" tick={{ fontSize: 12, fill: "#6B7280" }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 12, fill: "#6B7280" }} axisLine={false} tickLine={false} tickFormatter={(v) => `₹${(v / 100000).toFixed(0)}L`} />
              <Tooltip formatter={(v: any) => [`₹${((v as number) / 100000).toFixed(2)}L`]} contentStyle={{ borderRadius: 12, border: "1px solid #E5E7EB", fontSize: 12 }} />
              <Bar dataKey="revenue" fill="#155E4B" radius={[6, 6, 0, 0]} name="Revenue" />
              <Bar dataKey="expense" fill="#E5E7EB" radius={[6, 6, 0, 0]} name="Expenses" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="ndl-card p-5">
          <h2 className="ndl-section-title mb-1">Profit Trend</h2>
          <p className="text-sm text-text-secondary mb-5">Net profit by month</p>
          <ResponsiveContainer width="100%" height={240}>
            <AreaChart data={monthlyRevenue.map((d) => ({ ...d, profit: d.revenue - d.expense }))} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="profitGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#D4AF37" stopOpacity={0.2} />
                  <stop offset="95%" stopColor="#D4AF37" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
              <XAxis dataKey="month" tick={{ fontSize: 12, fill: "#6B7280" }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 12, fill: "#6B7280" }} axisLine={false} tickLine={false} tickFormatter={(v) => `₹${(v / 100000).toFixed(0)}L`} />
              <Tooltip formatter={(v: any) => [`₹${((v as number) / 100000).toFixed(2)}L`]} contentStyle={{ borderRadius: 12, border: "1px solid #E5E7EB", fontSize: 12 }} />
              <Area type="monotone" dataKey="profit" stroke="#D4AF37" strokeWidth={2.5} fill="url(#profitGrad)" name="Net Profit" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Transactions Table */}
      <div className="ndl-card overflow-hidden">
        <div className="flex items-center justify-between px-5 py-4 border-b border-border">
          <h2 className="ndl-section-title">Recent Transactions</h2>
          <button className="ndl-btn-secondary text-xs px-3 py-1.5">View All</button>
        </div>
        <table className="ndl-table">
          <thead><tr><th>Description</th><th>Category</th><th>Date</th><th>Type</th><th>Amount</th></tr></thead>
          <tbody>
            {transactions.map((t) => (
              <tr key={t.id}>
                <td>
                  <p className="text-sm font-medium text-text-primary">{t.description}</p>
                  <p className="text-xs text-text-secondary font-mono">{t.id}</p>
                </td>
                <td><span className="ndl-badge ndl-badge-secondary">{t.category}</span></td>
                <td className="text-sm text-text-secondary">{t.date}</td>
                <td>
                  <span className={`ndl-badge text-xs ${t.type === "income" ? "ndl-badge-success" : "ndl-badge-danger"}`}>
                    {t.type === "income" ? <ArrowUpRight size={11} /> : <ArrowDownRight size={11} />}
                    {t.type === "income" ? "Income" : "Expense"}
                  </span>
                </td>
                <td className={`text-sm font-bold ${t.type === "income" ? "text-success" : "text-danger"}`}>
                  {t.type === "income" ? "+" : "-"}₹{t.amount.toLocaleString("en-IN")}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
