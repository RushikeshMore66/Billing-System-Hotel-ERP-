"use client";

import { Sparkles, TrendingUp, BedDouble, UtensilsCrossed, Users, AlertTriangle, Lightbulb, ArrowRight } from "lucide-react";

const insights = [
  {
    category: "Revenue Optimization",
    icon: TrendingUp,
    color: "#155E4B",
    bg: "#EDF7F3",
    border: "#D0EDE5",
    impact: "High",
    impactColor: "#DC2626",
    title: "Weekend Rate Increase Opportunity",
    summary: "Weekend occupancy has been 23% above weekday average for the past 3 weekends. Your current weekend rate of ₹12,500 is 18% below comparable properties in the area.",
    recommendation: "Increase weekend room rates by ₹800–₹1,200 for the next 4 Fridays and Saturdays. Estimated additional revenue: ₹48,000–₹72,000.",
    metrics: [{ label: "Current Occ.", value: "91%" }, { label: "Avg Market Rate", value: "₹14,800" }, { label: "Your Rate", value: "₹12,500" }],
  },
  {
    category: "Food & Beverage",
    icon: UtensilsCrossed,
    color: "#D4AF37",
    bg: "#FFFBEB",
    border: "#FEF3C7",
    impact: "Medium",
    impactColor: "#F59E0B",
    title: "Top Dishes Driving Revenue",
    summary: "Butter Chicken (₹420) and Paneer Tikka (₹320) collectively account for 38% of restaurant revenue. Both have high margins and consistent demand.",
    recommendation: "Prioritize inventory for these items. Consider creating combo deals with these bestsellers at a 5–8% bundle discount to increase average order value.",
    metrics: [{ label: "Butter Chicken", value: "142 orders/wk" }, { label: "Paneer Tikka", value: "118 orders/wk" }, { label: "Combined Revenue", value: "₹1.1L/wk" }],
  },
  {
    category: "Occupancy",
    icon: BedDouble,
    color: "#49617A",
    bg: "#EEF1F5",
    border: "#D5DCE7",
    impact: "Medium",
    impactColor: "#F59E0B",
    title: "3 Rooms Vacant 4+ Days",
    summary: "Rooms 201, 305, and 410 have been unoccupied for 4 or more days. Based on booking patterns, these rooms have a lower booking rate than similar room types.",
    recommendation: "Run a targeted promotion on Booking.com and direct channels with a 12% discount for these specific room numbers for the next 7 days.",
    metrics: [{ label: "Vacant Days", value: "4–6 days" }, { label: "Revenue Lost", value: "~₹72,000" }, { label: "Recovery Potential", value: "₹52,000+" }],
  },
  {
    category: "Operations Alert",
    icon: AlertTriangle,
    color: "#DC2626",
    bg: "#FEF2F2",
    border: "#FEE2E2",
    impact: "Urgent",
    impactColor: "#DC2626",
    title: "Inventory Reorder Required",
    summary: "Basmati Rice (4kg remaining, min: 10kg) and Olive Oil (2L remaining, min: 5L) are critically low. Current stock will be exhausted within 1–2 days at current consumption rate.",
    recommendation: "Place emergency reorder with Agro Traders and Fine Foods immediately. Estimated reorder amounts: Basmati Rice 50kg, Olive Oil 15L.",
    metrics: [{ label: "Basmati Rice", value: "4kg left" }, { label: "Olive Oil", value: "2L left" }, { label: "Days to Depletion", value: "1–2 days" }],
  },
  {
    category: "Guest Experience",
    icon: Users,
    color: "#7C3AED",
    bg: "#F5F3FF",
    border: "#EDE9FE",
    impact: "Low",
    impactColor: "#16A34A",
    title: "High Guest Satisfaction Week",
    summary: "Average guest rating this week: 4.7/5. Positive reviews mention room cleanliness (92%), food quality (88%), and staff hospitality (95%). Two reviews specifically commended Ramesh Patil.",
    recommendation: "Recognize Ramesh Patil and the housekeeping team for their performance. Consider sharing the positive reviews in the team meeting to maintain morale.",
    metrics: [{ label: "Avg Rating", value: "4.7 / 5" }, { label: "Reviews This Week", value: "23" }, { label: "Response Rate", value: "91%" }],
  },
  {
    category: "Smart Suggestion",
    icon: Lightbulb,
    color: "#0EA5E9",
    bg: "#F0F9FF",
    border: "#BAE6FD",
    impact: "Low",
    impactColor: "#16A34A",
    title: "Upsell Opportunity: Room Upgrades",
    summary: "14 upcoming reservations are for Standard rooms while 3 Superior rooms are still available for the same dates. Standard guests could be offered upgrades at a nominal premium.",
    recommendation: "Send pre-arrival email offering room upgrade from Standard to Superior at ₹1,500 additional per night. Estimated additional revenue if 30% convert: ₹12,600.",
    metrics: [{ label: "Eligible Guests", value: "14" }, { label: "Available Upgrades", value: "3 rooms" }, { label: "Revenue Potential", value: "₹12,600" }],
  },
];

const impactBadgeStyle: Record<string, string> = {
  High: "bg-danger-50 text-danger",
  Medium: "bg-warning-50 text-warning",
  Urgent: "bg-danger-50 text-danger",
  Low: "bg-success-50 text-success",
};

export default function AIInsightsPage() {
  return (
    <div className="p-6 space-y-5 animate-fade-in">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center rounded-2xl" style={{ width: 48, height: 48, background: "linear-gradient(135deg, #7C3AED, #9d5bf7)", boxShadow: "0 4px 12px rgba(124,58,237,0.25)" }}>
            <Sparkles size={22} className="text-white" />
          </div>
          <div>
            <h1 className="ndl-page-title">AI Business Insights</h1>
            <p className="text-text-secondary text-sm mt-0.5">Powered by NiralayOS Intelligence Engine — Updated daily at 6:00 AM</p>
          </div>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg" style={{ background: "#F5F3FF", border: "1px solid #EDE9FE" }}>
          <div className="w-2 h-2 rounded-full animate-pulse" style={{ background: "#7C3AED" }} />
          <span className="text-xs font-semibold" style={{ color: "#7C3AED" }}>6 insights today</span>
        </div>
      </div>

      {/* Summary bar */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: "Urgent Actions", value: "1", color: "#DC2626", bg: "#FEF2F2" },
          { label: "High Impact", value: "1", color: "#F59E0B", bg: "#FFFBEB" },
          { label: "Optimization Tips", value: "2", color: "#155E4B", bg: "#EDF7F3" },
          { label: "Positive Signals", value: "2", color: "#7C3AED", bg: "#F5F3FF" },
        ].map((s) => (
          <div key={s.label} className="ndl-card p-4" style={{ background: s.bg }}>
            <p className="text-2xl font-bold" style={{ color: s.color }}>{s.value}</p>
            <p className="text-xs text-text-secondary mt-1">{s.label}</p>
          </div>
        ))}
      </div>

      {/* Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {insights.map((insight, i) => (
          <div key={i} className="ndl-card p-5 flex flex-col gap-4" style={{ background: insight.bg, borderColor: insight.border }}>
            <div className="flex items-start gap-3">
              <div className="flex items-center justify-center rounded-xl shrink-0"
                style={{ width: 40, height: 40, background: `${insight.color}20` }}>
                <insight.icon size={18} style={{ color: insight.color }} />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-[10px] font-bold uppercase tracking-widest" style={{ color: insight.color }}>
                    {insight.category}
                  </span>
                  <span className={`ndl-badge text-[10px] font-bold ${impactBadgeStyle[insight.impact]}`}>
                    {insight.impact} Impact
                  </span>
                </div>
                <h3 className="font-bold text-text-primary mt-1">{insight.title}</h3>
              </div>
            </div>

            <p className="text-sm text-text-secondary leading-relaxed">{insight.summary}</p>

            {/* Metrics */}
            <div className="flex items-center gap-3 flex-wrap">
              {insight.metrics.map((m) => (
                <div key={m.label} className="flex flex-col bg-white rounded-lg px-3 py-2 border border-border/50">
                  <span className="text-[10px] text-text-secondary">{m.label}</span>
                  <span className="text-sm font-bold text-text-primary">{m.value}</span>
                </div>
              ))}
            </div>

            {/* Recommendation */}
            <div className="rounded-xl p-3 bg-white border border-border/50">
              <p className="text-[10px] font-bold uppercase tracking-widest text-text-secondary mb-1">Recommendation</p>
              <p className="text-sm text-text-primary leading-relaxed">{insight.recommendation}</p>
            </div>

            <button className="flex items-center gap-1.5 text-sm font-semibold self-start transition-colors" style={{ color: insight.color }}>
              Take Action <ArrowRight size={14} />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
