import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";

export function HistoryPage() {
  const [q, setQ] = useState("");
  const { data } = useQuery({
    queryKey: ["history", q],
    queryFn: async () => (await api.get("/api/v1/history/conversations", { params: { q } })).data,
  });

  return (
    <div className="space-y-4">
      <h1 className="font-heading text-3xl">Conversation History</h1>
      <input className="w-full rounded-xl border border-border bg-card px-4 py-3" placeholder="Search conversations" value={q} onChange={(e) => setQ(e.target.value)} />

      <div className="grid gap-3">
        {(data ?? []).map((item: any) => (
          <div key={item.id} className="glass rounded-2xl p-4">
            <p className="font-medium">{item.title}</p>
            <p className="text-xs opacity-70">{item.subject} | {new Date(item.created_at).toLocaleString()}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
