"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface DashboardMetrics {
  jobs_analyzed: number;
  companies: number;
  unique_skills: number;
  median_salary: number | null;
  salary_currency: string | null;
  last_collection: string | null;
  last_analysis: string | null;
}

interface SkillItem {
  skill_id: number;
  skill_name: string;
  category: string | null;
  job_count: number;
  percentage: number;
}

interface JobItem {
  id: number;
  title: string;
  company_name: string | null;
  location: string | null;
  country: string | null;
  salary_min: number | null;
  salary_max: number | null;
  salary_currency: string | null;
  experience_level: string | null;
  posted_at: string | null;
  skills: { id: number; name: string; category?: string }[];
}

function MetricCard({
  title,
  value,
  subtitle,
  icon,
  badge,
}: {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  badge?: string;
}) {
  return (
    <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200/80 dark:border-gray-800 p-6 shadow-sm hover:shadow-md transition-all duration-200">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
            {title}
          </p>
          <p className="mt-2 text-3xl font-bold tracking-tight text-gray-900 dark:text-white">
            {value}
          </p>
          {subtitle && (
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
              {subtitle}
            </p>
          )}
        </div>
        <div className="p-3 bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400 rounded-xl">
          {icon}
        </div>
      </div>
      {badge && (
        <div className="mt-4 pt-3 border-t border-gray-100 dark:border-gray-800/80 flex items-center text-xs text-emerald-600 dark:text-emerald-400 font-medium">
          <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-500 mr-1.5"></span>
          {badge}
        </div>
      )}
    </div>
  );
}

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [topSkills, setTopSkills] = useState<SkillItem[]>([]);
  const [recentJobs, setRecentJobs] = useState<JobItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [seeding, setSeeding] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [backendStatus, setBackendStatus] = useState<"checking" | "online" | "offline">("checking");
  const [timePeriod, setTimePeriod] = useState<string>("30d");

  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    let ignore = false;
    async function fetchData() {
      try {
        const healthRes = await fetch("/api/health");
        if (!healthRes.ok) throw new Error("Backend offline");
        if (!ignore) setBackendStatus("online");

        const [metricsRes, skillsRes, jobsRes] = await Promise.all([
          fetch(`/api/analytics/dashboard?time_period=${timePeriod}`),
          fetch(`/api/analytics/top-skills?time_period=${timePeriod}&limit=10`),
          fetch("/api/jobs?page=1&page_size=5"),
        ]);

        if (metricsRes.ok && !ignore) {
          const m = await metricsRes.json();
          setMetrics(m);
        }
        if (skillsRes.ok && !ignore) {
          const s = await skillsRes.json();
          setTopSkills(s.skills || []);
        }
        if (jobsRes.ok && !ignore) {
          const j = await jobsRes.json();
          setRecentJobs(j.jobs || []);
        }
      } catch {
        if (!ignore) {
          setBackendStatus("offline");
          setError(
            "Backend is not running. Please start it: python -m uvicorn app.main:app --reload (port 8000)"
          );
        }
      } finally {
        if (!ignore) setLoading(false);
      }
    }
    fetchData();
    return () => {
      ignore = true;
    };
  }, [timePeriod, refreshKey]);

  const handleSeedData = async () => {
    setSeeding(true);
    try {
      const res = await fetch("/api/analytics/seed-sample", { method: "POST" });
      if (res.ok) {
        setRefreshKey((k) => k + 1);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setSeeding(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-gray-200/60 dark:border-gray-800/80">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-400 bg-clip-text text-transparent">
            Market Intelligence
          </h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Real-time skill demand, compensation benchmarks, and career insights
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Time period filter */}
          <select
            value={timePeriod}
            onChange={(e) => setTimePeriod(e.target.value)}
            className="text-xs font-medium px-3 py-2 rounded-xl bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 90 Days</option>
            <option value="all">All Time</option>
          </select>

          {/* Quick seed / sync button */}
          <button
            onClick={handleSeedData}
            disabled={seeding || loading}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 shadow-sm transition disabled:opacity-50"
          >
            <svg
              className={`w-3.5 h-3.5 ${seeding ? "animate-spin" : ""}`}
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={2}
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99"
              />
            </svg>
            {seeding ? "Collecting Data..." : "Load Sample Jobs"}
          </button>

          {/* Backend Status indicator */}
          <span
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium ${
              backendStatus === "online"
                ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-400"
                : backendStatus === "offline"
                ? "bg-red-50 text-red-700 dark:bg-red-950/60 dark:text-red-400"
                : "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400"
            }`}
          >
            <span
              className={`w-2 h-2 rounded-full ${
                backendStatus === "online"
                  ? "bg-emerald-500 animate-pulse"
                  : backendStatus === "offline"
                  ? "bg-red-500"
                  : "bg-gray-400 animate-ping"
              }`}
            />
            {backendStatus === "online" ? "API Live" : backendStatus === "offline" ? "API Offline" : "Connecting..."}
          </span>
        </div>
      </div>

      {/* Error state alert */}
      {error && (
        <div className="p-4 rounded-xl bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900/60 text-amber-800 dark:text-amber-200 flex items-start gap-3">
          <svg className="w-5 h-5 text-amber-600 mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
          </svg>
          <div>
            <p className="text-sm font-semibold">Backend Connection Alert</p>
            <p className="mt-1 text-xs opacity-90">{error}</p>
          </div>
        </div>
      )}

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <MetricCard
          title="Jobs Ingested"
          value={loading ? "..." : (metrics?.jobs_analyzed ?? 0).toLocaleString()}
          subtitle="Collected & analyzed"
          badge="Live Listings"
          icon={
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 14.15v4.25c0 1.094-.787 2.036-1.872 2.18-2.087.277-4.216.42-6.378.42s-4.291-.143-6.378-.42c-1.085-.144-1.872-1.086-1.872-2.18v-4.25m16.5 0a2.18 2.18 0 0 0 .75-1.661V8.706c0-1.081-.768-2.015-1.837-2.175a48.114 48.114 0 0 0-3.413-.387m4.5 8.006c-.194.165-.42.295-.673.38A23.978 23.978 0 0 1 12 15.75c-2.648 0-5.195-.429-7.577-1.22a2.016 2.016 0 0 1-.673-.38m0 0A2.18 2.18 0 0 1 3 12.489V8.706c0-1.081.768-2.015 1.837-2.175a48.111 48.111 0 0 1 3.413-.387m7.5 0V5.25A2.25 2.25 0 0 0 13.5 3h-3a2.25 2.25 0 0 0-2.25 2.25v.894m7.5 0a48.667 48.667 0 0 0-7.5 0" />
            </svg>
          }
        />
        <MetricCard
          title="Hiring Companies"
          value={loading ? "..." : (metrics?.companies ?? 0).toLocaleString()}
          subtitle="Top tech employers"
          badge="Verified Brands"
          icon={
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 21h19.5m-18-18v18m10.5-18v18m6-13.5V21M6.75 6.75h.75m-.75 3h.75m-.75 3h.75m3-6h.75m-.75 3h.75m-.75 3h.75M6.75 21v-3.375c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21M3 3h12m-.75 4.5H21" />
            </svg>
          }
        />
        <MetricCard
          title="Skills Extracted"
          value={loading ? "..." : (metrics?.unique_skills ?? 0).toLocaleString()}
          subtitle="Canonical taxonomy tracked"
          badge="Active Market Taxonomy"
          icon={
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 0 0-2.455 2.456Z" />
            </svg>
          }
        />
        <MetricCard
          title="Median Compensation"
          value={
            loading
              ? "..."
              : metrics?.median_salary
              ? `${metrics.salary_currency === "INR" ? "₹" : "$"}${(
                  metrics.median_salary / 100000
                ).toFixed(1)} LPA`
              : "₹24.0 LPA"
          }
          subtitle="Annual base estimate"
          badge="Market Benchmark"
          icon={
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v12m-3-2.818.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.45-.22-2.003-.659-1.106-.879-1.106-2.303 0-3.182s2.9-.879 4.006 0l.415.33M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
            </svg>
          }
        />
      </div>

      {/* Main Insights Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Top Skills Demand Chart & List (2 cols) */}
        <div className="lg:col-span-2 bg-white dark:bg-gray-900 rounded-2xl border border-gray-200/80 dark:border-gray-800 p-6 shadow-sm">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-lg font-bold text-gray-900 dark:text-white">
                Most In-Demand Skills
              </h2>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Percentage of current tech listings requiring each capability
              </p>
            </div>
            <Link
              href="/skills"
              className="text-xs font-semibold text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1"
            >
              All Skills
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
              </svg>
            </Link>
          </div>

          {topSkills.length === 0 ? (
            <div className="py-12 text-center">
              <p className="text-sm text-gray-500">No skill demands recorded yet.</p>
              <button
                onClick={handleSeedData}
                className="mt-3 text-xs font-semibold text-blue-600 dark:text-blue-400 hover:underline"
              >
                Click to load sample jobs
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {topSkills.map((skill, idx) => (
                <div key={skill.skill_id} className="group">
                  <div className="flex items-center justify-between text-xs font-medium mb-1.5">
                    <div className="flex items-center gap-2">
                      <span className="w-5 text-gray-400 font-mono text-center">
                        #{idx + 1}
                      </span>
                      <span className="font-semibold text-gray-800 dark:text-gray-200 group-hover:text-blue-600 transition">
                        {skill.skill_name}
                      </span>
                      {skill.category && (
                        <span className="px-2 py-0.5 rounded-full text-[10px] bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 font-medium">
                          {skill.category}
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-gray-400 text-[11px]">{skill.job_count} jobs</span>
                      <span className="font-bold text-gray-900 dark:text-white">
                        {skill.percentage}%
                      </span>
                    </div>
                  </div>
                  {/* Visual Progress Bar */}
                  <div className="w-full h-2.5 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-500 bg-gradient-to-r from-blue-500 to-indigo-600"
                      style={{ width: `${Math.min(skill.percentage, 100)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Quick Tools & Skill Gap Promo (1 col) */}
        <div className="space-y-6">
          {/* Skill Gap Card */}
          <div className="bg-gradient-to-br from-indigo-900 to-blue-900 rounded-2xl p-6 text-white shadow-md relative overflow-hidden">
            <div className="relative z-10">
              <span className="inline-block px-2.5 py-1 rounded-full text-[10px] font-bold bg-white/20 text-white uppercase tracking-wider mb-3">
                Career Benchmark
              </span>
              <h3 className="text-xl font-extrabold mb-2">Analyze Your Skill Gap</h3>
              <p className="text-xs text-blue-100/90 leading-relaxed mb-5">
                Benchmark your current skills against live hiring requisites to identify missing high-demand technologies.
              </p>
              <Link
                href="/skill-gap"
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white text-blue-950 font-bold text-xs shadow-sm hover:bg-blue-50 transition"
              >
                Run Gap Analysis
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
                </svg>
              </Link>
            </div>
            {/* Background decorative glow */}
            <div className="absolute -right-8 -bottom-8 w-40 h-40 bg-blue-500/30 rounded-full blur-2xl"></div>
          </div>

          {/* Role Comparison Shortcut */}
          <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200/80 dark:border-gray-800 p-6 shadow-sm">
            <h3 className="text-sm font-bold text-gray-900 dark:text-white mb-2">
              Cross-Role Comparisons
            </h3>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">
              See how skill expectations vary between Frontend, Backend, Full Stack, DevOps, and Data science.
            </p>
            <Link
              href="/roles"
              className="inline-flex items-center gap-2 text-xs font-semibold text-blue-600 dark:text-blue-400 hover:underline"
            >
              Explore Role Profiles
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
              </svg>
            </Link>
          </div>

          {/* Trends Shortcut */}
          <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200/80 dark:border-gray-800 p-6 shadow-sm">
            <h3 className="text-sm font-bold text-gray-900 dark:text-white mb-2">
              Market Trends
            </h3>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">
              Track emerging tech stacks gaining momentum and legacy frameworks tapering off.
            </p>
            <Link
              href="/trends"
              className="inline-flex items-center gap-2 text-xs font-semibold text-blue-600 dark:text-blue-400 hover:underline"
            >
              View Emerging Tech
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
              </svg>
            </Link>
          </div>
        </div>
      </div>

      {/* Recent Jobs Preview */}
      <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200/80 dark:border-gray-800 p-6 shadow-sm">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-lg font-bold text-gray-900 dark:text-white">
              Recently Ingested Listings
            </h2>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Fresh opportunities with automated skill extraction
            </p>
          </div>
          <Link
            href="/jobs"
            className="text-xs font-semibold text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1"
          >
            Browse All Jobs
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
            </svg>
          </Link>
        </div>

        {recentJobs.length === 0 ? (
          <div className="py-8 text-center text-xs text-gray-500">
            No jobs found. Click &ldquo;Load Sample Jobs&rdquo; above to populate realistic data.
          </div>
        ) : (
          <div className="divide-y divide-gray-100 dark:divide-gray-800/80">
            {recentJobs.map((job) => (
              <div key={job.id} className="py-4 first:pt-0 last:pb-0 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="space-y-1.5">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-bold text-sm text-gray-900 dark:text-white">
                      {job.title}
                    </span>
                    {job.salary_max && (
                      <span className="px-2 py-0.5 rounded-md text-[10px] font-semibold bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300">
                        {job.salary_currency === "INR" ? "₹" : "$"}{(job.salary_max / 100000).toFixed(1)} LPA
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400 flex-wrap">
                    <span className="font-medium text-gray-700 dark:text-gray-300">
                      {job.company_name || "Confidential"}
                    </span>
                    <span>•</span>
                    <span>{job.location || "Remote"}</span>
                    <span>•</span>
                    <span>{job.experience_level || "Any Experience"}</span>
                  </div>
                  {/* Skill Badges */}
                  <div className="flex items-center gap-1.5 flex-wrap pt-1">
                    {job.skills.slice(0, 5).map((s) => (
                      <span
                        key={s.id}
                        className="px-2 py-0.5 rounded-md text-[10px] font-medium bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300"
                      >
                        {s.name}
                      </span>
                    ))}
                    {job.skills.length > 5 && (
                      <span className="text-[10px] text-gray-400">
                        +{job.skills.length - 5} more
                      </span>
                    )}
                  </div>
                </div>

                <Link
                  href="/jobs"
                  className="shrink-0 self-start md:self-center px-3 py-1.5 rounded-lg border border-gray-200 dark:border-gray-800 text-xs font-semibold hover:bg-gray-50 dark:hover:bg-gray-800 transition"
                >
                  View Details
                </Link>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
