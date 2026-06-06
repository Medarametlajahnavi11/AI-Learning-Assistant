import { Link, Outlet, useLocation } from "react-router-dom";
import { motion } from "framer-motion";
import { BarChart3, BookOpen, FileStack, History, MessageSquare, User } from "lucide-react";

import { useUIStore } from "@/store/ui-store";

const nav = [
  { to: "/dashboard", label: "Dashboard", icon: BarChart3 },
  { to: "/chat", label: "Chat", icon: MessageSquare },
  { to: "/documents", label: "Knowledge Vault", icon: FileStack },
  { to: "/history", label: "History", icon: History },
  { to: "/profile", label: "Profile", icon: User },
];

export function AppShell() {
  const { pathname } = useLocation();
  const theme = useUIStore((s) => s.theme);
  const setTheme = useUIStore((s) => s.setTheme);

  return (
    <div className="min-h-screen px-4 py-4 md:px-8">
      <div className="glass mx-auto grid min-h-[92vh] max-w-7xl grid-cols-1 overflow-hidden rounded-3xl md:grid-cols-[260px_1fr]">
        <aside className="border-b border-border p-5 md:border-b-0 md:border-r">
          <div className="mb-8 flex items-center gap-2 font-heading text-xl font-semibold">
            <BookOpen className="text-accent" />
            LearnOS
          </div>

          <nav className="space-y-2">
            {nav.map((item) => {
              const active = pathname.startsWith(item.to);
              const Icon = item.icon;
              return (
                <Link
                  key={item.to}
                  to={item.to}
                  className="relative block overflow-hidden rounded-xl"
                >
                  {active && (
                    <motion.div
                      layoutId="active-nav"
                      className="absolute inset-0 bg-accent/15"
                      transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                    />
                  )}
                  <span className="relative flex items-center gap-2 px-4 py-3">
                    <Icon size={17} /> {item.label}
                  </span>
                </Link>
              );
            })}
          </nav>

          <button
            onClick={() => setTheme(theme === "light" ? "dark" : "light")}
            className="mt-6 w-full rounded-xl border border-border px-4 py-2 text-sm"
          >
            {theme === "light" ? "Enable Dark Mode" : "Enable Light Mode"}
          </button>
        </aside>

        <main className="p-4 md:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
