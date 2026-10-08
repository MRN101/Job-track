"use client";

import { useEffect, useState } from "react";

interface Profile {
  name: string;
  country: string;
  experience_level: string;
  target_roles: string[];
  skills: string[];
}

interface CollectorInfo {
  name: string;
  title: string;
  configured: boolean;
  description: string;
}

export default function SettingsPage() {
  const [profile, setProfile] = useState<Profile>({
    name: "",
    country: "India",
    experience_level: "0-2 years",
    target_roles: ["Software Engineer"],
    skills: [],
  });

  const [collectors, setCollectors] = useState<CollectorInfo[]>([]);
  const [selectedSource, setSelectedSource] = useState("sample");
  const [collectionRole, setCollectionRole] = useState("Software Engineer");
  const [collectionCountry, setCollectionCountry] = useState("India");
  const [maxResults, setMaxResults] = useState(25);

  const [savingProfile, setSavingProfile] = useState(false);
  const [collecting, setCollecting] = useState(false);
  const [collectionStatus, setCollectionStatus] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const [profRes, collRes] = await Promise.all([
          fetch("/api/profile"),
          fetch("/api/analytics/collectors"),
        ]);
        if (profRes.ok) {
          const p = await profRes.json();
          setProfile(p);
        }
        if (collRes.ok) {
          const c = await collRes.json();
          setCollectors(c || []);
        }
      } catch (e) {
        console.error(e);
      }
    }
    loadData();
  }, []);

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingProfile(true);
    setMessage(null);
    try {
      const res = await fetch("/api/profile", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(profile),
      });
      if (res.ok) {
        setMessage("Profile updated successfully!");
        setTimeout(() => setMessage(null), 3000);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setSavingProfile(false);
    }
  };

  const handleRunCollection = async () => {
    setCollecting(true);
    setCollectionStatus(null);
    try {
      const res = await fetch(`/api/analytics/collect?source=${selectedSource}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          country: collectionCountry,
          role: collectionRole,
          max_results: maxResults,
        }),
      });
      const data = await res.json();
      if (res.ok) {
        setCollectionStatus(
          `Collection complete! Retrieved: ${data.retrieved}, New Jobs: ${data.new_jobs}, Duplicates: ${data.duplicates}`
        );
      } else {
        setCollectionStatus(`Error: ${data.detail || data.message || "Failed"}`);
      }
    } catch (e: unknown) {
      const err = e instanceof Error ? e.message : "Network error";
      setCollectionStatus(`Error: ${err}`);
    } finally {
      setCollecting(false);
    }
  };

  const handleSeedSample = async () => {
    setCollecting(true);
    try {
      const res = await fetch("/api/analytics/seed-sample", { method: "POST" });
      if (res.ok) {
        const data = await res.json();
        setCollectionStatus(
          `Sample data loaded successfully! Added ${data.jobs_ingested} jobs, ${data.taxonomy_skills_seeded} new skills.`
        );
      }
    } catch (e: unknown) {
      const err = e instanceof Error ? e.message : "Network error";
      setCollectionStatus(`Failed to load sample: ${err}`);
    } finally {
      setCollecting(false);
    }
  };

  return (
    <div className="space-y-8 max-w-4xl">
      {/* Header */}
      <div className="pb-2 border-b border-gray-200/60 dark:border-gray-800/80">
        <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-400 bg-clip-text text-transparent">
          Settings & Data Pipeline
        </h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Configure personal career target profiles, manage live data sources, and trigger collections
        </p>
      </div>

      {message && (
        <div className="p-4 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-900 text-xs font-semibold text-emerald-800 dark:text-emerald-300">
          {message}
        </div>
      )}

      {/* Profile Form */}
      <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200/80 dark:border-gray-800 p-6 shadow-sm space-y-4">
        <h2 className="text-base font-extrabold text-gray-900 dark:text-white">
          Personal Career Profile
        </h2>
        <p className="text-xs text-gray-500">
          Used to calibrate your baseline in the Skill Gap analysis module
        </p>

        <form onSubmit={handleSaveProfile} className="space-y-4 pt-2">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-gray-500 mb-1">
                Name
              </label>
              <input
                type="text"
                value={profile.name}
                onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                placeholder="Your name"
                className="w-full px-3.5 py-2 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-xs focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-gray-500 mb-1">
                Target Country
              </label>
              <input
                type="text"
                value={profile.country}
                onChange={(e) => setProfile({ ...profile, country: e.target.value })}
                placeholder="e.g. India, United States"
                className="w-full px-3.5 py-2 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-xs focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-gray-500 mb-1">
                Experience Level
              </label>
              <select
                value={profile.experience_level}
                onChange={(e) => setProfile({ ...profile, experience_level: e.target.value })}
                className="w-full px-3.5 py-2 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-xs focus:ring-2 focus:ring-blue-500"
              >
                <option value="0-2 years">0-2 years (Entry / Junior)</option>
                <option value="3-5 years">3-5 years (Mid-Level)</option>
                <option value="5+ years">5+ years (Senior / Lead)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-gray-500 mb-1">
                Primary Target Role
              </label>
              <input
                type="text"
                value={profile.target_roles[0] || ""}
                onChange={(e) =>
                  setProfile({
                    ...profile,
                    target_roles: [e.target.value],
                  })
                }
                placeholder="e.g. Software Engineer, Frontend Developer"
                className="w-full px-3.5 py-2 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-xs focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div className="pt-2">
            <button
              type="submit"
              disabled={savingProfile}
              className="px-5 py-2.5 rounded-xl text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 transition shadow-sm disabled:opacity-50"
            >
              {savingProfile ? "Saving..." : "Save Profile Settings"}
            </button>
          </div>
        </form>
      </div>

      {/* Data Collectors & Pipeline Execution */}
      <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200/80 dark:border-gray-800 p-6 shadow-sm space-y-6">
        <div>
          <h2 className="text-base font-extrabold text-gray-900 dark:text-white">
            Job Data Ingestion Pipeline
          </h2>
          <p className="text-xs text-gray-500">
            Collect live listings from APIs or load the curated dataset
          </p>
        </div>

        {/* Data Source Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {collectors.map((c) => (
            <div
              key={c.name}
              onClick={() => setSelectedSource(c.name)}
              className={`p-4 rounded-xl border cursor-pointer transition flex flex-col justify-between ${
                selectedSource === c.name
                  ? "border-blue-500 bg-blue-50/50 dark:bg-blue-950/20 shadow-sm"
                  : "border-gray-200 dark:border-gray-800 hover:border-gray-300"
              }`}
            >
              <div>
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-bold text-gray-900 dark:text-white">
                    {c.title}
                  </h3>
                  <span
                    className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                      c.configured
                        ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-400"
                        : "bg-amber-50 text-amber-700 dark:bg-amber-950 dark:text-amber-400"
                    }`}
                  >
                    {c.configured ? "Ready" : "API Key Required"}
                  </span>
                </div>
                <p className="text-[11px] text-gray-500 mt-1">{c.description}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Collection parameters */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
          <div>
            <label className="block text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1">
              Role Query
            </label>
            <input
              type="text"
              value={collectionRole}
              onChange={(e) => setCollectionRole(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-xs"
            />
          </div>
          <div>
            <label className="block text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1">
              Country
            </label>
            <input
              type="text"
              value={collectionCountry}
              onChange={(e) => setCollectionCountry(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-xs"
            />
          </div>
          <div>
            <label className="block text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1">
              Max Items
            </label>
            <input
              type="number"
              value={maxResults}
              onChange={(e) => setMaxResults(Number(e.target.value))}
              className="w-full px-3 py-2 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-xs"
            />
          </div>
        </div>

        {/* Buttons */}
        <div className="flex flex-wrap items-center gap-3 pt-2">
          <button
            onClick={handleRunCollection}
            disabled={collecting}
            className="px-5 py-2.5 rounded-xl text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 transition shadow-sm disabled:opacity-50"
          >
            {collecting ? "Collecting..." : "Run Job Collection"}
          </button>

          <button
            onClick={handleSeedSample}
            disabled={collecting}
            className="px-4 py-2.5 rounded-xl text-xs font-bold border border-gray-200 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800 transition"
          >
            Re-Seed Sample Dataset
          </button>
        </div>

        {collectionStatus && (
          <div className="p-3 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-xs font-medium text-gray-700 dark:text-gray-300">
            {collectionStatus}
          </div>
        )}
      </div>

      {/* Technical Architecture Notes */}
      <div className="p-5 rounded-2xl bg-gray-100 dark:bg-gray-900 border border-gray-200 dark:border-gray-800 text-xs text-gray-500 space-y-1">
        <p className="font-bold text-gray-800 dark:text-gray-200">
          Backend Architecture & Storage
        </p>
        <p>• Database: SQLite (local file at <code className="font-mono">backend/data/jobpulse.db</code>)</p>
        <p>• Skill Extraction: Canonical taxonomy dictionary with boundary regex matching + optional LLM analysis</p>
        <p>• API Docs: <a href="http://localhost:8000/api/docs" target="_blank" className="text-blue-500 underline">http://localhost:8000/api/docs</a></p>
      </div>
    </div>
  );
}
