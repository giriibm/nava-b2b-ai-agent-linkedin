"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { ICP } from "@/lib/types";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

const ORG_ID = "org-nava-tech"; // Phase 1: single-tenant; becomes dynamic in Phase 3

export default function ICPBuilderPage() {
  const [icps, setIcps] = useState<ICP[]>([]);
  const [name, setName] = useState("");
  const [industry, setIndustry] = useState("");
  const [geography, setGeography] = useState("");
  const [companySize, setCompanySize] = useState("");
  const [roles, setRoles] = useState("");
  const [challenges, setChallenges] = useState("");
  const [keywords, setKeywords] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = () => api.listICPs().then(setIcps).catch((e) => setError(String(e)));
  useEffect(() => { load(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await api.createICP({
        organization_id: ORG_ID,
        name,
        industry,
        geography,
        company_size_range: companySize,
        target_roles: roles.split(",").map((s) => s.trim()).filter(Boolean),
        business_challenges: challenges.split(",").map((s) => s.trim()).filter(Boolean),
        keywords: keywords.split(",").map((s) => s.trim()).filter(Boolean),
      });
      setName(""); setIndustry(""); setGeography(""); setCompanySize("");
      setRoles(""); setChallenges(""); setKeywords("");
      load();
    } catch (e) {
      setError(String(e));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-navy">ICP Builder</h1>
        <p className="text-gray-500 text-sm mt-1">
          Define the Ideal Customer Profile that drives prospect discovery and AI scoring.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader><CardTitle>New ICP</CardTitle></CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-3">
              <div>
                <Label htmlFor="name">Name</Label>
                <Input id="name" value={name} onChange={(e) => setName(e.target.value)} required
                  placeholder="e.g. Manufacturing — Arizona" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <Label htmlFor="industry">Industry</Label>
                  <Input id="industry" value={industry} onChange={(e) => setIndustry(e.target.value)} placeholder="Manufacturing" />
                </div>
                <div>
                  <Label htmlFor="geography">Geography</Label>
                  <Input id="geography" value={geography} onChange={(e) => setGeography(e.target.value)} placeholder="Arizona" />
                </div>
              </div>
              <div>
                <Label htmlFor="size">Company Size</Label>
                <Input id="size" value={companySize} onChange={(e) => setCompanySize(e.target.value)} placeholder="100-1000 employees" />
              </div>
              <div>
                <Label htmlFor="roles">Target Roles (comma-separated)</Label>
                <Input id="roles" value={roles} onChange={(e) => setRoles(e.target.value)} placeholder="CTO, VP Operations, Director IT" />
              </div>
              <div>
                <Label htmlFor="challenges">Business Challenges (comma-separated)</Label>
                <Input id="challenges" value={challenges} onChange={(e) => setChallenges(e.target.value)} placeholder="legacy systems, manual processes" />
              </div>
              <div>
                <Label htmlFor="keywords">Keywords (comma-separated)</Label>
                <Input id="keywords" value={keywords} onChange={(e) => setKeywords(e.target.value)} placeholder="generative AI, automation" />
              </div>
              {error && <p className="text-sm text-red-600">{error}</p>}
              <Button type="submit" disabled={submitting}>{submitting ? "Saving..." : "Create ICP"}</Button>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Existing ICPs</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {icps.length === 0 && <p className="text-sm text-gray-500">No ICPs defined yet.</p>}
            {icps.map((icp) => (
              <div key={icp.id} className="border border-gray-100 rounded-md p-3">
                <div className="font-medium">{icp.name}</div>
                <div className="text-xs text-gray-500 mt-1">
                  {icp.industry} · {icp.geography} · {icp.company_size_range}
                </div>
                {icp.target_roles.length > 0 && (
                  <div className="text-xs text-gray-600 mt-1">Roles: {icp.target_roles.join(", ")}</div>
                )}
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
