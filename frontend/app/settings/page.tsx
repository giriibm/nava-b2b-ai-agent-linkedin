"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function SettingsPage() {
  const [health, setHealth] = useState<{ status: string; llm_providers_available: string[] } | null>(null);
  const [salesforce, setSalesforce] = useState<{ configured: boolean } | null>(null);
  const [heyreach, setHeyreach] = useState<{ configured: boolean } | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.health().then(setHealth).catch((e) => setError(String(e)));
    api.salesforceStatus().then(setSalesforce).catch(() => {});
    api.heyreachStatus().then(setHeyreach).catch(() => {});
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-navy">Settings</h1>
        <p className="text-gray-500 text-sm mt-1">
          LLM provider and integration configuration. Values are set via backend .env — this
          view is read-only status, matching the LLM Gateway / Integration Service abstraction
          in the Master Spec.
        </p>
      </div>

      {error && <p className="text-sm text-red-600">Could not reach backend API: {error}</p>}

      <Card>
        <CardHeader><CardTitle>LLM Gateway</CardTitle></CardHeader>
        <CardContent>
          {!health ? <p className="text-sm text-gray-500">Loading...</p> : (
            <div className="text-sm space-y-1">
              <p>Backend status: <Badge>{health.status}</Badge></p>
              <p>Available providers: {health.llm_providers_available.join(", ")}</p>
              <p className="text-xs text-gray-500">Active provider is set via LLM_PROVIDER in backend/.env.</p>
            </div>
          )}
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader><CardTitle>Salesforce</CardTitle></CardHeader>
          <CardContent className="text-sm">
            {salesforce ? (
              <Badge status={salesforce.configured ? "converted" : "rejected"}>
                {salesforce.configured ? "Configured" : "Not configured"}
              </Badge>
            ) : <p className="text-gray-500">Loading...</p>}
            <p className="text-xs text-gray-500 mt-2">System of record for Leads, Accounts, Contacts, Opportunities.</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>HeyReach</CardTitle></CardHeader>
          <CardContent className="text-sm">
            {heyreach ? (
              <Badge status={heyreach.configured ? "converted" : "rejected"}>
                {heyreach.configured ? "Configured" : "Not configured"}
              </Badge>
            ) : <p className="text-gray-500">Loading...</p>}
            <p className="text-xs text-gray-500 mt-2">Delivers only human-approved LinkedIn outreach.</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
