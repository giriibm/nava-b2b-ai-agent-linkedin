"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { GeneratedMessage } from "@/lib/types";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

const REVIEWER = "sales-rep@navatech.com"; // Phase 1: replace with authenticated user identity

export default function ApprovalsPage() {
  const [queue, setQueue] = useState<GeneratedMessage[]>([]);
  const [edits, setEdits] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = () => api.approvalQueue().then(setQueue).catch((e) => setError(String(e)));
  useEffect(() => { load(); }, []);

  const approve = async (id: string) => {
    setBusy(id);
    try { await api.approveMessage(id, REVIEWER); load(); } catch (e) { setError(String(e)); }
    finally { setBusy(null); }
  };
  const saveEdit = async (id: string) => {
    setBusy(id);
    try { await api.editMessage(id, REVIEWER, edits[id]); load(); } catch (e) { setError(String(e)); }
    finally { setBusy(null); }
  };
  const reject = async (id: string) => {
    setBusy(id);
    try { await api.rejectMessage(id, REVIEWER, "Not relevant"); load(); } catch (e) { setError(String(e)); }
    finally { setBusy(null); }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-navy">Approval Queue</h1>
        <p className="text-gray-500 text-sm mt-1">
          Every AI-generated message stops here. Nothing is sent without an explicit human approval.
        </p>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {queue.length === 0 && (
        <Card><CardContent className="text-sm text-gray-500">Nothing pending review.</CardContent></Card>
      )}

      <div className="space-y-4">
        {queue.map((msg) => (
          <Card key={msg.id}>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="capitalize">{msg.message_type.replace("_", " ")} · {msg.channel}</CardTitle>
              <Badge status={msg.status}>{msg.status}</Badge>
            </CardHeader>
            <CardContent className="space-y-3">
              <Textarea
                defaultValue={msg.content}
                onChange={(e) => setEdits((prev) => ({ ...prev, [msg.id]: e.target.value }))}
                rows={3}
              />
              <div className="flex gap-2">
                <Button size="sm" onClick={() => approve(msg.id)} disabled={busy === msg.id}>Approve</Button>
                <Button size="sm" variant="outline" onClick={() => saveEdit(msg.id)} disabled={busy === msg.id || !edits[msg.id]}>
                  Save Edit
                </Button>
                <Button size="sm" variant="destructive" onClick={() => reject(msg.id)} disabled={busy === msg.id}>
                  Reject
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
