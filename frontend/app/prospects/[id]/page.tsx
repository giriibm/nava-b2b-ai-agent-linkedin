"use client";
import { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import { ProspectCompany, ProspectContactDetail } from "@/lib/types";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

function pollJob(jobId: string, onDone: () => void) {
  const interval = setInterval(async () => {
    const job = await api.getJob(jobId);
    if (job.status === "completed" || job.status === "failed") {
      clearInterval(interval);
      onDone();
    }
  }, 1500);
  return () => clearInterval(interval);
}

export default function ProspectDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [company, setCompany] = useState<ProspectCompany | null>(null);
  const [contacts, setContacts] = useState<Record<string, ProspectContactDetail>>({});
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(() => {
    api.getProspect(id).then(async (c) => {
      setCompany(c);
      const details = await Promise.all(c.contacts.map((ct) => api.getContact(ct.id)));
      setContacts(Object.fromEntries(details.map((d) => [d.id, d])));
    }).catch((e) => setError(String(e)));
  }, [id]);

  useEffect(() => { load(); }, [load]);

  const runResearch = async () => {
    if (!company) return;
    setBusy("research");
    try {
      const { job_id } = await api.triggerResearch(company.id);
      pollJob(job_id, () => { load(); setBusy(null); });
    } catch (e) { setError(String(e)); setBusy(null); }
  };

  const runScore = async (contactId: string) => {
    setBusy(`score-${contactId}`);
    try {
      const { job_id } = await api.triggerScoring(contactId);
      pollJob(job_id, () => { load(); setBusy(null); });
    } catch (e) { setError(String(e)); setBusy(null); }
  };

  const runGenerate = async (contactId: string) => {
    setBusy(`gen-${contactId}`);
    try {
      const { job_id } = await api.triggerPersonalization(contactId, "linkedin");
      pollJob(job_id, () => { load(); setBusy(null); });
    } catch (e) { setError(String(e)); setBusy(null); }
  };

  if (!company) return <p className="text-sm text-gray-500">Loading...</p>;
  const research = company.research_records[company.research_records.length - 1];

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-navy">{company.name}</h1>
          <p className="text-gray-500 text-sm mt-1">
            {company.industry || "—"} · {company.location || "—"} · {company.employee_count ?? "?"} employees
          </p>
        </div>
        <Badge status={company.stage}>{company.stage}</Badge>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>AI Research</CardTitle>
          <Button size="sm" onClick={runResearch} disabled={busy === "research"}>
            {busy === "research" ? "Researching..." : "Run Research Agent"}
          </Button>
        </CardHeader>
        <CardContent>
          {!research ? (
            <p className="text-sm text-gray-500">No research yet.</p>
          ) : (
            <div className="space-y-2 text-sm">
              <p>{research.summary}</p>
              <p><span className="font-medium">Business challenges:</span> {research.business_challenges.join(", ") || "—"}</p>
              <p><span className="font-medium">AI opportunity areas:</span> {research.ai_opportunity_areas.join(", ") || "—"}</p>
              <p><span className="font-medium">Recommended solution:</span> {research.recommended_solution}</p>
              <p className="text-xs text-gray-400">Model: {research.model_used}</p>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Contacts</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          {company.contacts.length === 0 && <p className="text-sm text-gray-500">No contacts on this account yet.</p>}
          {company.contacts.map((ct) => {
            const detail = contacts[ct.id];
            const latestScore = detail?.scores[detail.scores.length - 1];
            return (
              <div key={ct.id} className="border border-gray-100 rounded-md p-3 space-y-2">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium">{ct.full_name}</div>
                    <div className="text-xs text-gray-500">{ct.title}</div>
                  </div>
                  <div className="flex gap-2">
                    <Button size="sm" variant="outline" onClick={() => runScore(ct.id)} disabled={busy === `score-${ct.id}`}>
                      {busy === `score-${ct.id}` ? "Scoring..." : "Score"}
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => runGenerate(ct.id)} disabled={busy === `gen-${ct.id}`}>
                      {busy === `gen-${ct.id}` ? "Generating..." : "Generate Messages"}
                    </Button>
                  </div>
                </div>
                {latestScore && (
                  <div className="text-sm">
                    <span className="font-semibold">AI Fit Score: {latestScore.score}/100</span>
                    <p className="text-gray-600 text-xs mt-1">{latestScore.reasoning}</p>
                  </div>
                )}
                {detail?.messages && detail.messages.length > 0 && (
                  <div className="space-y-1 pt-1">
                    {detail.messages.map((m) => (
                      <div key={m.id} className="text-xs bg-gray-50 rounded p-2">
                        <div className="flex justify-between">
                          <span className="font-medium">{m.message_type}</span>
                          <Badge status={m.status}>{m.status}</Badge>
                        </div>
                        <p className="mt-1 text-gray-700">{m.content}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </CardContent>
      </Card>
    </div>
  );
}
