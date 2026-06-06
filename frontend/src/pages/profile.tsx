import { FormEvent, useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

export function ProfilePage() {
  const toast = useToast();
  const queryClient = useQueryClient();

  const { data } = useQuery({
    queryKey: ["profile"],
    queryFn: async () => (await api.get("/api/v1/profile")).data,
  });

  const [learningLevel, setLearningLevel] = useState("High School");
  const [style, setStyle] = useState("Step-by-Step");
  const [mode, setMode] = useState("Knowledge Vault");
  const [subjects, setSubjects] = useState("Physics, Mathematics");
  const [dailyGoal, setDailyGoal] = useState(3);

  useEffect(() => {
    if (data) {
      setLearningLevel(data.learning_level);
      setStyle(data.preferred_explanation_style);
      setMode(data.preferred_learning_mode);
      setSubjects((data.subjects ?? []).join(", "));
      setDailyGoal(data.daily_goal ?? 3);
    }
  }, [data]);

  const save = useMutation({
    mutationFn: async () => {
      await api.put("/api/v1/profile", {
        learning_level: learningLevel,
        preferred_explanation_style: style,
        preferred_learning_mode: mode,
        subjects: subjects.split(",").map((s) => s.trim()).filter(Boolean),
        daily_goal: dailyGoal,
      });
    },
    onSuccess: async () => {
      toast.success("Profile updated");
      await queryClient.invalidateQueries({ queryKey: ["profile"] });
    },
    onError: () => toast.error("Failed to update profile"),
  });

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    save.mutate();
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <h1 className="font-heading text-3xl">Learning Profile</h1>
      <div className="glass grid gap-3 rounded-2xl p-4 md:grid-cols-2">
        <input value={learningLevel} onChange={(e) => setLearningLevel(e.target.value)} className="rounded-xl border border-border bg-card px-4 py-3" placeholder="Learning level" />
        <input value={style} onChange={(e) => setStyle(e.target.value)} className="rounded-xl border border-border bg-card px-4 py-3" placeholder="Explanation style" />
        <input value={mode} onChange={(e) => setMode(e.target.value)} className="rounded-xl border border-border bg-card px-4 py-3" placeholder="Learning mode" />
        <input value={subjects} onChange={(e) => setSubjects(e.target.value)} className="rounded-xl border border-border bg-card px-4 py-3" placeholder="Subjects" />
        <input type="number" value={dailyGoal} onChange={(e) => setDailyGoal(Number(e.target.value))} className="rounded-xl border border-border bg-card px-4 py-3" placeholder="Daily goal" />
      </div>
      <button className="rounded-xl bg-accent px-4 py-2 text-white">Save Preferences</button>
    </form>
  );
}
