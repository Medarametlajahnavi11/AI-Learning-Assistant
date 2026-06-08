import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";

import { api } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import { useAuthStore } from "@/store/auth-store";

export function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const setToken = useAuthStore((s) => s.setToken);
  const toast = useToast();
  const navigate = useNavigate();

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    try {
      const { data } = await api.post("/api/v1/auth/login", { email, password });
      setToken(data.access_token, data.refresh_token);
      toast.success("Welcome back");
      navigate("/dashboard");
    } catch {
      toast.error("Unable to log in");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <motion.form
        onSubmit={onSubmit}
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass w-full max-w-md rounded-2xl p-8"
      >
        <h1 className="mb-6 font-heading text-3xl">Sign In</h1>
        <div className="space-y-4">
          <input className="w-full rounded-xl border border-border bg-card px-4 py-3" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
          <input className="w-full rounded-xl border border-border bg-card px-4 py-3" type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
          <button disabled={loading} className="w-full rounded-xl bg-accent px-4 py-3 text-white">
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </div>
        <p className="mt-4 text-sm">
          New learner? <Link className="text-accent" to="/signup">Create account</Link>
        </p>
      </motion.form>
    </div>
  );
}
