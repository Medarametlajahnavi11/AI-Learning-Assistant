import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis } from "recharts";

import { api } from "@/lib/api";

export function DashboardPage() {
  const { data } = useQuery({
    queryKey: ["dashboard-overview"],
    queryFn: async () => (await api.get("/api/v1/dashboard/overview")).data,
  });

  const weekly = data?.weekly ?? [];

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
      <div>
        <h1 className="font-heading text-3xl">Learning Dashboard</h1>
        <p className="text-sm opacity-80">Track streaks, XP, subject mastery, and weekly momentum.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        {[
          { label: "Questions", value: data?.questions_asked ?? 0 },
          { label: "Documents", value: data?.documents_uploaded ?? 0 },
          { label: "Streak", value: data?.learning_streak ?? 0 },
          { label: "Total XP", value: data?.total_xp ?? 0 },
        ].map((item, idx) => (
          <motion.div key={item.label} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.08 }} className="glass rounded-2xl p-4 shadow-glow">
            <p className="text-sm opacity-70">{item.label}</p>
            <p className="font-heading text-3xl">{item.value}</p>
          </motion.div>
        ))}
      </div>

      <div className="glass rounded-2xl p-4">
        <h2 className="mb-3 font-heading text-xl">Weekly Learning Summary</h2>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={weekly}>
              <defs>
                <linearGradient id="xp" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="hsl(var(--accent))" stopOpacity={0.65} />
                  <stop offset="95%" stopColor="hsl(var(--accent))" stopOpacity={0.05} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date_key" />
              <Tooltip />
              <Area type="monotone" dataKey="xp_earned" stroke="hsl(var(--accent))" fill="url(#xp)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </motion.div>
  );
}
