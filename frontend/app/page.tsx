"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { ProspectCompany, ICP } from "@/lib/types";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function DashboardPage() {
  const [icps, setIcps] = useState<ICP[]>([]);
  const [prospects, setProspects] = useState<ProspectCompany[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([api.listICPs(), api.listProspects()])
      .then(([icpData, prospectData]) => {
        setIcps(icpData);
        setProspects(prospectData);
      })
      .catch((e) => setError(String(e)));
  }, []);

  const stageCounts = prospects.reduce<Record<string, number>>((acc, p) => {
    acc[p.stage] = (acc[p.stage] || 0) + 1;
    return acc;
  }, {});

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-navy">Dashboard</h1>
        <p className="text-gray-500 text-sm mt-1">
          Pipeline overview across active ICPs and prospects.
        </p>
      </div>

      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="text-red-700 text-sm">
            Could not reach the backend API ({error}). Make sure it's running at{" "}
            <code>NEXT_PUBLIC_API_BASE_URL</code>.
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader><CardTitle>Active ICPs</CardTitle></CardHeader>
          <CardContent className="text-3xl font-bold">{icps.length}</CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Prospect Companies</CardTitle></CardHeader>
          <CardContent className="text-3xl font-bold">{prospects.length}</CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Approved / Contacted</CardTitle></CardHeader>
          <CardContent className="text-3xl font-bold">
            {(stageCounts["approved"] || 0) + (stageCounts["contacted"] || 0)}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader><CardTitle>Pipeline by Stage</CardTitle></CardHeader>
        <CardContent>
          {Object.keys(stageCounts).length === 0 ? (
            <p className="text-sm text-gray-500">
              No prospects yet — start by defining an ICP and importing companies.
            </p>
          ) : (
            <div className="flex flex-wrap gap-3">
              {Object.entries(stageCounts).map(([stage, count]) => (
                <div key={stage} className="flex items-center gap-2">
                  <Badge status={stage}>{stage}</Badge>
                  <span className="text-sm font-medium">{count}</span>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
