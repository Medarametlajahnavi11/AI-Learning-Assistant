import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";

import { api } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import { useAuthStore } from "@/store/auth-store";

const levels = ["Elementary", "Middle School", "High School", "Undergraduate", "Graduate", "Professional"];
const styles = ["Step-by-Step", "Visual Explanation", "Exam Preparation", "Real World Examples", "Beginner Friendly", "Advanced Technical"];
const modes = ["Knowledge Vault", "Global Scholar"];

export function SignupPage() {
  const [step, setStep] = useState(1);
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [learningLevel, setLearningLevel] = useState(levels[2]);
  const [subjects, setSubjects] = useState("Physics, Mathematics");
  const [style, setStyle] = useState(styles[0]);
  const [mode, setMode] = useState(modes[0]);
  const [loading, setLoading] = useState(false);

  const toast = useToast();
  const navigate = useNavigate();
  const setToken = useAuthStore((s) => s.setToken);

  async function finishSignup(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    try {
      const payload = {
        account: { full_name: fullName, email, password },
        learning: { learning_level: learningLevel },
        preferences: {
          subjects: subjects.split(",").map((s) => s.trim()).filter(Boolean),
          preferred_explanation_style: style,
          preferred_learning_mode: "Knowledge Vault", // Default
        },
      };
      const { data } = await api.post("/api/v1/auth/signup", payload);
      
      if (data.requires_confirmation) {
        toast.success("Account created! Please check your email to confirm your account.");
        navigate("/login");
      } else {
        setToken(data.access_token);
        toast.success("Account created");
        navigate("/dashboard");
      }
    } catch {
      toast.error("Signup failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <motion.form onSubmit={finishSignup} initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass w-full max-w-2xl rounded-2xl p-8">
        <h1 className="mb-2 font-heading text-3xl">Create Learning Account</h1>
        <p className="mb-6 text-sm opacity-80">Step {step} of 3</p>

        {step === 1 && (
          <div className="grid gap-4 md:grid-cols-2">
            <input className="rounded-xl border border-border bg-card px-4 py-3" placeholder="Full Name" value={fullName} onChange={(e) => setFullName(e.target.value)} />
            <input className="rounded-xl border border-border bg-card px-4 py-3" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
            <input className="rounded-xl border border-border bg-card px-4 py-3 md:col-span-2" type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
          </div>
        )}

        {step === 2 && (
          <select className="w-full rounded-xl border border-border bg-card px-4 py-3" value={learningLevel} onChange={(e) => setLearningLevel(e.target.value)}>
            {levels.map((l) => (
              <option key={l} value={l}>{l}</option>
            ))}
          </select>
        )}

        {step === 3 && (
          <div className="space-y-4">
            <input className="w-full rounded-xl border border-border bg-card px-4 py-3" placeholder="Subjects (comma separated)" value={subjects} onChange={(e) => setSubjects(e.target.value)} />
            <select className="w-full rounded-xl border border-border bg-card px-4 py-3" value={style} onChange={(e) => setStyle(e.target.value)}>
              {styles.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>
        )}

        <div className="mt-6 flex justify-between">
          <button type="button" disabled={step === 1} onClick={() => setStep((s) => Math.max(1, s - 1))} className="rounded-xl border border-border px-4 py-2">
            Back
          </button>
          {step < 3 ? (
            <button type="button" onClick={() => setStep((s) => Math.min(3, s + 1))} className="rounded-xl bg-accent px-4 py-2 text-white">Next</button>
          ) : (
            <button type="submit" disabled={loading} className="rounded-xl bg-accent px-4 py-2 text-white">{loading ? "Creating..." : "Create Account"}</button>
          )}
        </div>
      </motion.form>
    </div>
  );
}
