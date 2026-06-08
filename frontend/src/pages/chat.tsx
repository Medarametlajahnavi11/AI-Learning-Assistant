import { FormEvent, useMemo, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { api } from "@/lib/api";
import { clearAuthTokens } from "@/lib/auth";
import { useToast } from "@/hooks/use-toast";

const subjects = ["Mathematics", "Physics", "Chemistry", "Biology", "Programming", "Economics", "Business", "History", "Geography"];
const levels = ["Elementary", "Middle School", "High School", "Undergraduate", "Graduate", "Professional"];
const styles = ["Step-by-Step", "Visual Explanation", "Exam Preparation", "Real World Examples", "Beginner Friendly", "Advanced Technical"];

export function ChatPage() {
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [message, setMessage] = useState("");
  const [subject, setSubject] = useState(subjects[0]);
  const [level, setLevel] = useState(levels[2]);
  const [explanationStyle, setExplanationStyle] = useState(styles[0]);
  const [learningMode, setLearningMode] = useState<"Knowledge Vault" | "Global Scholar">("Knowledge Vault");
  const [streaming, setStreaming] = useState(false);
  const toast = useToast();
  const queryClient = useQueryClient();

  const { data: messages } = useQuery({
    queryKey: ["messages", conversationId],
    queryFn: async () => {
      if (!conversationId) return [];
      return (await api.get(`/api/v1/chat/conversations/${conversationId}/messages`)).data;
    },
    enabled: Boolean(conversationId),
  });

  const renderedMessages = useMemo(() => messages ?? [], [messages]);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (!message.trim() || streaming) return;

    setStreaming(true);
    try {
      const accessToken = localStorage.getItem("access_token");
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
      };
      if (accessToken) {
        headers.Authorization = `Bearer ${accessToken}`;
      }

      const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/v1/chat/stream`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          conversation_id: conversationId,
          message,
          subject,
          learning_level: level,
          explanation_style: explanationStyle,
          learning_mode: learningMode,
        }),
      });

      if (res.status === 401) {
        clearAuthTokens();
        window.location.replace("/login");
        return;
      }

      if (!res.ok) {
        throw new Error("Chat request failed");
      }

      if (!res.body) throw new Error("Missing stream body");
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let assistant = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const events = chunk.split("\n\n").filter(Boolean);
        for (const eventText of events) {
          const dataLine = eventText.split("\n").find((line) => line.startsWith("data: "));
          if (!dataLine) continue;
          const payload = JSON.parse(dataLine.slice(6));
          if (payload.type === "meta" && payload.conversation_id) {
            setConversationId(payload.conversation_id);
          }
          if (payload.type === "token") {
            assistant += payload.value;
          }
        }
      }

      setMessage("");
      await queryClient.invalidateQueries({ queryKey: ["messages", conversationId] });
      await queryClient.invalidateQueries({ queryKey: ["dashboard-overview"] });
      if (assistant.trim().length === 0) {
        toast.info("No response text generated");
      }
    } catch {
      toast.error("Chat request failed");
    } finally {
      setStreaming(false);
    }
  }

  return (
    <div className="grid gap-4 lg:grid-cols-[1fr_340px]">
      <div className="glass flex h-[78vh] flex-col rounded-2xl">
        <div className="border-b border-border p-3 text-sm opacity-80">AI Tutor Conversation</div>
        <div className="flex-1 space-y-4 overflow-auto p-4">
          {renderedMessages.map((msg: any) => (
            <div key={msg.id} className={msg.role === "user" ? "text-right" : "text-left"}>
              <div className={msg.role === "user" ? "ml-auto inline-block max-w-[85%] rounded-2xl bg-accent px-4 py-3 text-white" : "inline-block max-w-[85%] rounded-2xl border border-border bg-card px-4 py-3"}>
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
              </div>
            </div>
          ))}
        </div>

        <form onSubmit={onSubmit} className="border-t border-border p-3">
          <div className="mb-3 flex gap-2">
            {["Knowledge Vault", "Global Scholar"].map((m) => (
              <button
                key={m}
                type="button"
                onClick={() => setLearningMode(m as any)}
                className={`rounded-lg px-3 py-1 text-xs font-medium transition-colors ${
                  learningMode === m ? "bg-accent text-white" : "bg-card border border-border opacity-60 hover:opacity-100"
                }`}
              >
                {m}
              </button>
            ))}
          </div>
          <div className="flex gap-2">
            <input value={message} onChange={(e) => setMessage(e.target.value)} placeholder="Ask a question..." className="flex-1 rounded-xl border border-border bg-card px-3 py-3" />
            <button disabled={streaming} className="rounded-xl bg-accent px-4 py-3 text-white">{streaming ? "Thinking..." : "Send"}</button>
          </div>
        </form>
      </div>

      <aside className="glass space-y-3 rounded-2xl p-4">
        <h2 className="font-heading text-xl">Learning Controls</h2>
        <select className="w-full rounded-xl border border-border bg-card px-3 py-2" value={subject} onChange={(e) => setSubject(e.target.value)}>{subjects.map((s) => <option key={s}>{s}</option>)}</select>
        <select className="w-full rounded-xl border border-border bg-card px-3 py-2" value={level} onChange={(e) => setLevel(e.target.value)}>{levels.map((l) => <option key={l}>{l}</option>)}</select>
        <select className="w-full rounded-xl border border-border bg-card px-3 py-2" value={explanationStyle} onChange={(e) => setExplanationStyle(e.target.value)}>{styles.map((s) => <option key={s}>{s}</option>)}</select>
      </aside>
    </div>
  );
}
