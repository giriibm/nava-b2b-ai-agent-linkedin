"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { ICP, ProspectCompany } from "@/lib/types";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function ProspectsPage() {
  const [prospects, setProspects] = useState<ProspectCompany[]>([]);
  const [icps, setIcps] = useState<ICP[]>([]);
  const [icpId, setIcpId] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [website, setWebsite] = useState("");
  const [contactName, setContactName] = useState("");
  const [contactTitle, setContactTitle] = useState("");
  const [linkedinUrl, setLinkedinUrl] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    api.listProspects().then(setProspects).catch((e) => setError(String(e)));
    api.listICPs().then(setIcps).catch(() => {});
  };
  useEffect(() => { load(); }, []);

  const handleImport = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!icpId) { setError("Select an ICP first (create one in the ICP Builder)."); return; }
    setSubmitting(true);
    setError(null);
    try {
      await api.importProspect({
        icp_id: icpId,
        name: companyName,
        website,
        contacts: contactName ? [{ full_name: contactName, title: contactTitle, linkedin_url: linkedinUrl }] : [],
      });
      setCompanyName(""); setWebsite(""); setContactName(""); setContactTitle(""); setLinkedinUrl("");
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
        <h1 className="text-2xl font-bold text-navy">Prospect Workspace</h1>
        <p className="text-gray-500 text-sm mt-1">
          Companies and contacts imported from LinkedIn Sales Navigator exports.
        </p>
      </div>

      <Card>
        <CardHeader><CardTitle>Import Prospect</CardTitle></CardHeader>
        <CardContent>
          <form onSubmit={handleImport} className="grid grid-cols-1 md:grid-cols-3 gap-3 items-end">
            <div>
              <Label htmlFor="icp">ICP</Label>
              <select id="icp" value={icpId} onChange={(e) => setIcpId(e.target.value)}
                className="flex h-9 w-full rounded-md border border-gray-300 bg-white px-3 py-1 text-sm">
                <option value="">Select ICP...</option>
                {icps.map((icp) => <option key={icp.id} value={icp.id}>{icp.name}</option>)}
              </select>
            </div>
            <div>
              <Label htmlFor="companyName">Company Name</Label>
              <Input id="companyName" value={companyName} onChange={(e) => setCompanyName(e.target.value)} required />
            </div>
            <div>
              <Label htmlFor="website">Website</Label>
              <Input id="website" value={website} onChange={(e) => setWebsite(e.target.value)} placeholder="https://..." />
            </div>
            <div>
              <Label htmlFor="contactName">Contact Name</Label>
              <Input id="contactName" value={contactName} onChange={(e) => setContactName(e.target.value)} />
            </div>
            <div>
              <Label htmlFor="contactTitle">Contact Title</Label>
              <Input id="contactTitle" value={contactTitle} onChange={(e) => setContactTitle(e.target.value)} placeholder="CTO" />
            </div>
            <div>
              <Label htmlFor="linkedinUrl">LinkedIn URL</Label>
              <Input id="linkedinUrl" value={linkedinUrl} onChange={(e) => setLinkedinUrl(e.target.value)} placeholder="https://linkedin.com/in/..." />
            </div>
            <div className="md:col-span-3">
              {error && <p className="text-sm text-red-600 mb-2">{error}</p>}
              <Button type="submit" disabled={submitting}>{submitting ? "Importing..." : "Import"}</Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>All Prospects</CardTitle></CardHeader>
        <CardContent className="space-y-2">
          {prospects.length === 0 && <p className="text-sm text-gray-500">No prospects imported yet.</p>}
          {prospects.map((p) => (
            <Link key={p.id} href={`/prospects/${p.id}`}
              className="flex items-center justify-between border border-gray-100 rounded-md p-3 hover:bg-gray-50">
              <div>
                <div className="font-medium">{p.name}</div>
                <div className="text-xs text-gray-500">
                  {p.industry || "—"} · {p.location || "—"} · {p.contacts.length} contact(s)
                </div>
              </div>
              <Badge status={p.stage}>{p.stage}</Badge>
            </Link>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
