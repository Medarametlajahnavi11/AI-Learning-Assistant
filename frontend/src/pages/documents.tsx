import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

export function DocumentsPage() {
  const [file, setFile] = useState<File | null>(null);
  const toast = useToast();
  const queryClient = useQueryClient();

  const { data } = useQuery({
    queryKey: ["documents"],
    queryFn: async () => (await api.get("/api/v1/documents")).data,
  });

  const upload = useMutation({
    mutationFn: async () => {
      if (!file) return;
      const form = new FormData();
      form.append("file", file);
      await api.post("/api/v1/documents/upload", form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
    },
    onSuccess: async () => {
      toast.success("Document uploaded and indexed");
      setFile(null);
      await queryClient.invalidateQueries({ queryKey: ["documents"] });
      await queryClient.invalidateQueries({ queryKey: ["dashboard-overview"] });
    },
    onError: () => toast.error("Upload failed"),
  });

  const deleteDoc = useMutation({
    mutationFn: async (documentId: string) => {
      await api.delete(`/api/v1/documents/${documentId}`);
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["documents"] });
      toast.success("Document deleted");
    },
  });

  function submit(event: FormEvent) {
    event.preventDefault();
    upload.mutate();
  }

  return (
    <div className="space-y-4">
      <h1 className="font-heading text-3xl">Knowledge Vault</h1>
      <form onSubmit={submit} className="glass flex flex-wrap items-center gap-3 rounded-2xl p-4">
        <input type="file" accept=".pdf,.docx,.pptx,.txt" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
        <button className="rounded-xl bg-accent px-4 py-2 text-white">{upload.isPending ? "Processing..." : "Upload + Index"}</button>
      </form>

      <div className="grid gap-3">
        {(data ?? []).map((doc: any) => (
          <div key={doc.document_id} className="glass flex items-center justify-between rounded-2xl p-4">
            <div>
              <p className="font-medium">{doc.filename}</p>
              <p className="text-xs opacity-70">Embedding: {doc.embedding_status} | Index: {doc.indexing_status} | Status: {doc.processing_status}</p>
            </div>
            <button onClick={() => deleteDoc.mutate(doc.document_id)} className="rounded-xl border border-border px-3 py-1">Delete</button>
          </div>
        ))}
      </div>
    </div>
  );
}
