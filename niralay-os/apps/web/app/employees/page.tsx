"use client";

import { useState } from "react";
import { Users, Plus, Search, Phone, Mail, Clock, CheckCircle2, UserX } from "lucide-react";

const employees = [
  { id: "EMP-001", name: "Ramesh Patil", role: "Head Waiter", dept: "Restaurant", phone: "+91 98765 43210", email: "ramesh@niralay.com", shift: "Morning", status: "on-duty", joined: "Jan 2022", avatar: "RP" },
  { id: "EMP-002", name: "Sunita Rao", role: "Receptionist", dept: "Front Desk", phone: "+91 87654 32109", email: "sunita@niralay.com", shift: "Morning", status: "on-duty", joined: "Mar 2021", avatar: "SR" },
  { id: "EMP-003", name: "Vikash Kumar", role: "Chef (Senior)", dept: "Kitchen", phone: "+91 76543 21098", email: "vikash@niralay.com", shift: "Morning", status: "on-duty", joined: "Jun 2020", avatar: "VK" },
  { id: "EMP-004", name: "Priya Desai", role: "Housekeeper", dept: "Housekeeping", phone: "+91 65432 10987", email: "priya@niralay.com", shift: "Morning", status: "on-duty", joined: "Sep 2022", avatar: "PD" },
  { id: "EMP-005", name: "Sunil Mehta", role: "Waiter", dept: "Restaurant", phone: "+91 54321 09876", email: "sunil@niralay.com", shift: "Evening", status: "off-duty", joined: "Nov 2021", avatar: "SM" },
  { id: "EMP-006", name: "Ananya Singh", role: "Accountant", dept: "Finance", phone: "+91 43210 98765", email: "ananya@niralay.com", shift: "Morning", status: "on-duty", joined: "Feb 2023", avatar: "AS" },
  { id: "EMP-007", name: "Deepak Verma", role: "Security Guard", dept: "Security", phone: "+91 32109 87654", email: "deepak@niralay.com", shift: "Night", status: "off-duty", joined: "Aug 2021", avatar: "DV" },
  { id: "EMP-008", name: "Kavita Sharma", role: "Housekeeper", dept: "Housekeeping", phone: "+91 21098 76543", email: "kavita@niralay.com", shift: "Morning", status: "on-leave", joined: "Apr 2022", avatar: "KS" },
  { id: "EMP-009", name: "Rajan Nair", role: "Bartender", dept: "Restaurant", phone: "+91 10987 65432", email: "rajan@niralay.com", shift: "Evening", status: "on-duty", joined: "Dec 2020", avatar: "RN" },
  { id: "EMP-010", name: "Meena Joshi", role: "Chef (Junior)", dept: "Kitchen", phone: "+91 09876 54321", email: "meena@niralay.com", shift: "Morning", status: "on-duty", joined: "Jul 2023", avatar: "MJ" },
];

const deptColors: Record<string, string> = {
  Restaurant: "#155E4B",
  "Front Desk": "#49617A",
  Kitchen: "#D4AF37",
  Housekeeping: "#7C3AED",
  Finance: "#0EA5E9",
  Security: "#DC2626",
};

const statusConfig: Record<string, { label: string; className: string; icon: React.ElementType }> = {
  "on-duty": { label: "On Duty", className: "ndl-badge-success", icon: CheckCircle2 },
  "off-duty": { label: "Off Duty", className: "ndl-badge-secondary", icon: Clock },
  "on-leave": { label: "On Leave", className: "ndl-badge-warning", icon: UserX },
};

export default function EmployeesPage() {
  const [search, setSearch] = useState("");
  const [deptFilter, setDeptFilter] = useState("all");
  const [view, setView] = useState<"grid" | "table">("grid");

  const depts = ["all", ...Array.from(new Set(employees.map((e) => e.dept)))];
  const filtered = employees.filter((e) => {
    const matchSearch = e.name.toLowerCase().includes(search.toLowerCase()) || e.role.toLowerCase().includes(search.toLowerCase());
    const matchDept = deptFilter === "all" || e.dept === deptFilter;
    return matchSearch && matchDept;
  });

  return (
    <div className="p-6 space-y-5 animate-fade-in">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="ndl-page-title">Employees</h1>
          <p className="text-text-secondary text-sm mt-1">Staff roster, shifts, and HR management</p>
        </div>
        <button className="ndl-btn-primary gap-2"><Plus size={16} /> Add Employee</button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: "Total Staff", value: employees.length, icon: Users, color: "#49617A" },
          { label: "On Duty", value: employees.filter((e) => e.status === "on-duty").length, icon: CheckCircle2, color: "#155E4B" },
          { label: "Off Duty", value: employees.filter((e) => e.status === "off-duty").length, icon: Clock, color: "#6B7280" },
          { label: "On Leave", value: employees.filter((e) => e.status === "on-leave").length, icon: UserX, color: "#F59E0B" },
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

      {/* Filters */}
      <div className="flex items-center gap-3 flex-wrap">
        <div className="relative">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-secondary pointer-events-none" />
          <input type="text" placeholder="Search staff…" value={search} onChange={(e) => setSearch(e.target.value)}
            className="pl-9 pr-4 py-2 bg-surface border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all" />
        </div>
        <div className="flex items-center gap-1.5">
          {depts.map((d) => (
            <button key={d} onClick={() => setDeptFilter(d)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${deptFilter === d ? "bg-primary text-white" : "bg-surface border border-border text-text-secondary hover:bg-background"}`}>
              {d === "all" ? "All Departments" : d}
            </button>
          ))}
        </div>
      </div>

      {/* Employee Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {filtered.map((emp) => {
          const cfg = statusConfig[emp.status];
          const deptColor = deptColors[emp.dept] ?? "#6B7280";
          return (
            <div key={emp.id} className="ndl-card p-5 flex flex-col gap-4">
              <div className="flex items-start gap-3">
                <div className="flex items-center justify-center rounded-2xl font-bold text-white text-sm shrink-0"
                  style={{ width: 46, height: 46, background: `linear-gradient(135deg, ${deptColor}, ${deptColor}cc)` }}>
                  {emp.avatar}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-bold text-text-primary truncate">{emp.name}</p>
                  <p className="text-xs text-text-secondary truncate mt-0.5">{emp.role}</p>
                  <span className={`ndl-badge text-xs mt-1.5 inline-flex ${cfg.className}`}>
                    <cfg.icon size={10} />{cfg.label}
                  </span>
                </div>
              </div>

              <div className="space-y-1.5 text-sm">
                <div className="flex items-center gap-2 text-text-secondary">
                  <div className="w-3 h-3 rounded-sm shrink-0" style={{ background: `${deptColor}25` }}>
                    <div className="w-2 h-2 rounded-sm m-0.5" style={{ background: deptColor }} />
                  </div>
                  <span className="text-xs">{emp.dept}</span>
                  <span className="ml-auto text-xs">{emp.shift} Shift</span>
                </div>
                <div className="flex items-center gap-2 text-text-secondary">
                  <Phone size={12} className="shrink-0" />
                  <span className="text-xs truncate">{emp.phone}</span>
                </div>
                <div className="flex items-center gap-2 text-text-secondary">
                  <Mail size={12} className="shrink-0" />
                  <span className="text-xs truncate">{emp.email}</span>
                </div>
              </div>

              <div className="pt-3 border-t border-border flex items-center justify-between">
                <span className="text-xs text-text-secondary">Since {emp.joined}</span>
                <button className="text-xs text-primary font-semibold hover:underline">View Profile</button>
              </div>
            </div>
          );
        })}
      </div>

      {filtered.length === 0 && (
        <div className="flex flex-col items-center justify-center py-16 text-text-secondary">
          <Users size={40} className="mb-3 opacity-20" />
          <p className="text-sm font-medium">No employees found</p>
        </div>
      )}
    </div>
  );
}
