"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface DashboardMetrics {
  jobs_analyzed: number;
  companies: number;
  unique_skills: number;
  median_salary: number | null;
  salary_min: number | null;
  salary_max: number | null;
  salary_p25: number | null;
  salary_p75: number | null;
  salary_currency: string | null;
  jobs_with_salary: number;
  last_collection: string | null;
  last_analysis: string | null;
  data_type: "real" | "demo";
  is_demo: boolean;
  sources_breakdown: Record<string, number>;
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
  source: string;
  data_type: string;
  title: string;
  company_name: string | null;
  location: string | null;
  country: string | null;
  salary_min: number | null;
  salary_max: number | null;
  salary_currency: string | null;
  salary_period: string | null;
  salary_normalized: number | null;
  experience_level: string | null;
  posted_at: string | null;
  skills: { id: number; name: string; category?: string }[];
}

interface DataQualityMetrics {
  total_jobs: number;
  real_jobs: number;
  demo_jobs: number;
  jobs_with_description: number;
  jobs_with_salary: number;
  jobs_with_skills: number;
  roles_normalized?: number;
  locations_normalized?: number;
  duplicate_records_prevented?: number;
  sources_breakdown: Record<string, number>;
  last_collection_per_source: Record<string, string | null>;
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
  const [dataQuality, setDataQuality] = useState<DataQualityMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [collecting, setCollecting] = useState(false);
  const [backendStatus, setBackendStatus] = useState<"checking" | "online" | "offline">("checking");
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [isDemoMode, setIsDemoMode] = useState<boolean>(false);
  const [timePeriod, setTimePeriod] = useState<string>("30d");
  const [sourceFilter, setSourceFilter] = useState<string>("all");
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    let ignore = false;
    async function fetchData() {
      setLoading(true);
      setError(null);
      try {
        const healthRes = await fetch("/api/health");
        if (!healthRes.ok) throw new Error("Backend offline");
        if (!ignore) setBackendStatus("online");

        const demoParam = isDemoMode ? "&include_demo=true" : "";
        const sourceParam = sourceFilter !== "all" ? `&source=${sourceFilter}` : "";

        const [metricsRes, skillsRes, jobsRes, qualityRes] = await Promise.all([
          fetch(`/api/analytics/dashboard?time_period=${timePeriod}${demoParam}${sourceParam}`),
          fetch(`/api/analytics/top-skills?time_period=${timePeriod}&limit=10${demoParam}${sourceParam}`),
          fetch(`/api/jobs?page=1&page_size=6${demoParam}${sourceParam}`),
          fetch("/api/analytics/data-quality"),
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
        if (qualityRes.ok && !ignore) {
          const q = await qualityRes.json();
          setDataQuality(q);
        }
      } catch {
        if (!ignore) {
          setBackendStatus("offline");
          setError("Backend connection error. Please ensure FastAPI is running on port 8000.");
        }
      } finally {
        if (!ignore) setLoading(false);
      }
    }

    fetchData();
    return () => {
      ignore = true;
    };
  }, [timePeriod, sourceFilter, isDemoMode, refreshKey]);

  // Quick live trigger for Remotive
  const handleQuickCollect = async () => {
    setCollecting(true);
    try {
      const res = await fetch("/api/analytics/collect?source=remotive", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          country: "Worldwide",
          role: "Software Engineer",
          max_results: 50,
        }),
      });
      if (res.ok) {
        setIsDemoMode(false);
        setRefreshKey((k) => k + 1);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setCollecting(false);
    }
  };

  const formatSalary = (metricsData: DashboardMetrics | null) => {
    if (!metricsData || metricsData.median_salary === null || metricsData.jobs_with_salary === 0) {
      return "No data reported";
    }
    const val = metricsData.median_salary;
    if (metricsData.salary_currency === "INR") {
      return `₹${(val / 100000).toFixed(1)} LPA`;
    }
    return `$${val >= 1000 ? `${(val / 1000).toFixed(0)}k` : val.toLocaleString()}/yr`;
  };

  const formatPercentileRange = (metricsData: DashboardMetrics | null) => {
    if (
      !metricsData ||
      metricsData.salary_p25 === null ||
      metricsData.salary_p75 === null ||
      metricsData.jobs_with_salary === 0
    ) {
      return "Based on 0 reported listings";
    }
    if (metricsData.salary_currency === "INR") {
      return `25th–75th: ₹${(metricsData.salary_p25 / 100000).toFixed(1)}–₹${(
        metricsData.salary_p75 / 100000
      ).toFixed(1)} LPA (${metricsData.jobs_with_salary} listings)`;
    }
    return `25th–75th: $${Math.round(metricsData.salary_p25 / 1000)}k–$${Math.round(
      metricsData.salary_p75 / 1000
    )}k (${metricsData.jobs_with_salary} listings)`;
  };

  const hasJobs = (metrics?.jobs_analyzed ?? 0) > 0;

  return (
    <div className="space-y-8">
      {/* Top Header & Mode Selectors */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-4 border-b border-gray-200/80 dark:border-gray-800">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-400 bg-clip-text text-transparent">
              Market Intelligence
            </h1>
            {isDemoMode ? (
              <span className="px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 border border-amber-300 dark:border-amber-700">
                Demo Mode
              </span>
            ) : (
              <span className="px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-700">
                Live Real Data
              </span>
            )}
          </div>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {isDemoMode
              ? "Viewing curated sample developer jobs for development & preview."
              : "Live job market intelligence derived strictly from real listings."}
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex flex-wrap items-center gap-2.5">
          {/* Data Mode Switcher */}
          <div className="inline-flex p-1 rounded-xl bg-gray-100 dark:bg-gray-800/80 border border-gray-200 dark:border-gray-700 text-xs font-semibold">
            <button
              onClick={() => setIsDemoMode(false)}
              className={`px-3 py-1.5 rounded-lg transition ${
                !isDemoMode
                  ? "bg-white dark:bg-gray-900 text-blue-600 dark:text-blue-400 shadow-sm"
                  : "text-gray-500 hover:text-gray-900 dark:text-gray-400"
              }`}
            >
              Real Data
            </button>
            <button
              onClick={() => setIsDemoMode(true)}
              className={`px-3 py-1.5 rounded-lg transition ${
                isDemoMode
                  ? "bg-amber-500 text-white shadow-sm"
                  : "text-gray-500 hover:text-gray-900 dark:text-gray-400"
              }`}
            >
              Demo Dataset
            </button>
          </div>

          {/* Time Filter */}
          <select
            value={timePeriod}
            onChange={(e) => setTimePeriod(e.target.value)}
            className="text-xs font-medium px-3 py-2 rounded-xl bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 90 Days</option>
            <option value="6m">Last 6 Months</option>
            <option value="all">All Time</option>
          </select>

          {/* Source Filter */}
          <select
            value={sourceFilter}
            onChange={(e) => setSourceFilter(e.target.value)}
            className="text-xs font-medium px-3 py-2 rounded-xl bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Sources</option>
            <option value="remotive">Remotive (Live API)</option>
            <option value="adzuna">Adzuna</option>
            {isDemoMode && <option value="sample">Sample Curated</option>}
          </select>

          {/* Live Ingestion Button */}
          {!isDemoMode && (
            <button
              onClick={handleQuickCollect}
              disabled={collecting || loading}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 shadow-sm transition disabled:opacity-50"
            >
              <svg
                className={`w-3.5 h-3.5 ${collecting ? "animate-spin" : ""}`}
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={2}
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99" />
              </svg>
              {collecting ? "Collecting..." : "Collect Live Jobs"}
            </button>
          )}

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
            {backendStatus === "online" ? "API Live" : "API Offline"}
          </span>
        </div>
      </div>

      {/* Demo Mode Alert Banner */}
      {isDemoMode && (
        <div className="p-4 rounded-2xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800/80 text-amber-900 dark:text-amber-200 flex items-start justify-between gap-3 shadow-sm">
          <div className="flex items-start gap-3">
            <svg className="w-5 h-5 text-amber-600 mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
            </svg>
            <div>
              <p className="text-sm font-bold">Demo Data Active</p>
              <p className="text-xs opacity-90 mt-0.5">
                Analytics are currently displaying the curated sample dataset and are not based on live job market listings.
              </p>
            </div>
          </div>
          <button
            onClick={() => setIsDemoMode(false)}
            className="px-3 py-1 rounded-lg text-xs font-semibold bg-amber-200 dark:bg-amber-800 hover:bg-amber-300 transition text-amber-900 dark:text-amber-100 shrink-0"
          >
            Switch to Real Data
          </button>
        </div>
      )}

      {/* Error state */}
      {error && (
        <div className="p-4 rounded-xl bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900 text-red-800 dark:text-red-200 text-sm">
          {error}
        </div>
      )}

      {/* Empty State when no real jobs exist */}
      {!loading && !hasJobs ? (
        <div className="bg-white dark:bg-gray-900 rounded-3xl border border-gray-200 dark:border-gray-800 p-12 text-center space-y-5 shadow-sm max-w-2xl mx-auto my-8">
          <div className="w-16 h-16 rounded-2xl bg-blue-50 dark:bg-blue-950/50 flex items-center justify-center text-blue-600 mx-auto">
            <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 14.15v4.25c0 1.094-.787 2.036-1.872 2.18-2.087.277-4.216.42-6.378.42s-4.291-.143-6.378-.42c-1.085-.144-1.872-1.086-1.872-2.18v-4.25m16.5 0a2.18 2.18 0 0 0 .75-1.661V8.706c0-1.081-.768-2.015-1.837-2.175a48.114 48.114 0 0 0-3.413-.387m4.5 8.006c-.194.165-.42.295-.673.38A23.978 23.978 0 0 1 12 15.75c-2.648 0-5.195-.429-7.577-1.22a2.016 2.016 0 0 1-.673-.38m0 0A2.18 2.18 0 0 1 3 12.489V8.706c0-1.081.768-2.015 1.837-2.175a48.111 48.111 0 0 1 3.413-.387m7.5 0V5.25A2.25 2.25 0 0 0 13.5 3h-3a2.25 2.25 0 0 0-2.25 2.25v.894m7.5 0a48.667 48.667 0 0 0-7.5 0" />
            </svg>
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">
              {isDemoMode ? "No Demo Jobs Matching Filter" : "No Real Job Data Available Yet"}
            </h2>
            <p className="mt-2 text-sm text-gray-500 dark:text-gray-400 max-w-md mx-auto">
              {isDemoMode
                ? "No sample jobs match the selected filter parameters."
                : "JobPulse does not show fabricated numbers. Run a collection from live sources (Remotive open developer API or Adzuna) to populate real analytics, or switch to the Demo Dataset."}
            </p>
          </div>

          <div className="flex flex-wrap justify-center gap-3 pt-2">
            {!isDemoMode && (
              <button
                onClick={handleQuickCollect}
                disabled={collecting}
                className="px-5 py-2.5 rounded-xl text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 shadow-md transition disabled:opacity-50"
              >
                {collecting ? "Collecting Live Jobs..." : "Collect Live Jobs (Remotive)"}
              </button>
            )}
            <button
              onClick={() => setIsDemoMode(true)}
              className="px-5 py-2.5 rounded-xl text-xs font-semibold bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-200 transition"
            >
              Load Demo Dataset
            </button>
          </div>
        </div>
      ) : (
        <>
          {/* Metrics Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            <MetricCard
              title="Jobs Analyzed"
              value={loading ? "..." : (metrics?.jobs_analyzed ?? 0).toLocaleString()}
              subtitle={`Filter: ${timePeriod.toUpperCase()} window`}
              badge={isDemoMode ? "Demo Dataset" : "Live Market Listings"}
              icon={
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 14.15v4.25c0 1.094-.787 2.036-1.872 2.18-2.087.277-4.216.42-6.378.42s-4.291-.143-6.378-.42c-1.085-.144-1.872-1.086-1.872-2.18v-4.25m16.5 0a2.18 2.18 0 0 0 .75-1.661V8.706c0-1.081-.768-2.015-1.837-2.175a48.114 48.114 0 0 0-3.413-.387m4.5 8.006c-.194.165-.42.295-.673.38A23.978 23.978 0 0 1 12 15.75c-2.648 0-5.195-.429-7.577-1.22a2.016 2.016 0 0 1-.673-.38m0 0A2.18 2.18 0 0 1 3 12.489V8.706c0-1.081.768-2.015 1.837-2.175a48.111 48.111 0 0 1 3.413-.387m7.5 0V5.25A2.25 2.25 0 0 0 13.5 3h-3a2.25 2.25 0 0 0-2.25 2.25v.894m7.5 0a48.667 48.667 0 0 0-7.5 0" />
                </svg>
              }
            />

            <MetricCard
              title="Hiring Companies"
              value={loading ? "..." : (metrics?.companies ?? 0).toLocaleString()}
              subtitle="Distinct organizations"
              badge="Verified Employers"
              icon={
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 21h19.5m-18-18v18m10.5-18v18m6-13.5V21M6.75 6.75h.75m-.75 3h.75m-.75 3h.75m3-6h.75m-.75 3h.75m-.75 3h.75M6.75 21v-3.375c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21M3 3h12m-.75 4.5H21" />
                </svg>
              }
            />

            <MetricCard
              title="Skills Tracked"
              value={loading ? "..." : (metrics?.unique_skills ?? 0).toLocaleString()}
              subtitle="Canonical taxonomy matches"
              badge="Standardized Skills"
              icon={
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 0 0-2.455 2.456Z" />
                </svg>
              }
            />

            <MetricCard
              title="Median Compensation"
              value={loading ? "..." : formatSalary(metrics)}
              subtitle={formatPercentileRange(metrics)}
              badge="Statistical Percentiles"
              icon={
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v12m-3-2.818.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.45-.22-2.003-.659-1.106-.879-1.106-2.303 0-3.182s2.9-.879 4.006 0l.415.33M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                </svg>
              }
            />
          </div>

          {/* Sources & Data Quality Section */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Active Sources Status Card */}
            <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200/80 dark:border-gray-800 p-6 shadow-sm">
              <h2 className="text-sm font-bold text-gray-900 dark:text-white uppercase tracking-wider mb-4">
                Data Sources & Freshness
              </h2>
              <div className="space-y-3">
                {Object.entries(metrics?.sources_breakdown ?? {}).length === 0 ? (
                  <p className="text-xs text-gray-500">No source records for this filter.</p>
                ) : (
                  Object.entries(metrics?.sources_breakdown ?? {}).map(([src, count]) => (
                    <div key={src} className="flex items-center justify-between p-2.5 rounded-xl bg-gray-50 dark:bg-gray-800/50">
                      <div className="flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-blue-500"></span>
                        <span className="text-xs font-semibold capitalize text-gray-800 dark:text-gray-200">{src}</span>
                      </div>
                      <span className="text-xs font-bold text-gray-900 dark:text-white">{count} listings</span>
                    </div>
                  ))
                )}
              </div>
              <div className="mt-4 pt-3 border-t border-gray-100 dark:border-gray-800 text-xs text-gray-500 flex justify-between">
                <span>Last Collected:</span>
                <span className="font-medium text-gray-700 dark:text-gray-300">
                  {metrics?.last_collection
                    ? new Date(metrics.last_collection).toLocaleString()
                    : "Not recorded"}
                </span>
              </div>
            </div>

            {/* Data Quality & Integrity Card */}
            <div className="lg:col-span-2 bg-white dark:bg-gray-900 rounded-2xl border border-gray-200/80 dark:border-gray-800 p-6 shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-sm font-bold text-gray-900 dark:text-white uppercase tracking-wider">
                  Data Quality & Coverage Metrics
                </h2>
                <span className="text-[11px] text-gray-500 font-medium">
                  {dataQuality?.duplicate_records_prevented ?? 0} duplicates prevented
                </span>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
                <div className="p-3 rounded-xl bg-gray-50 dark:bg-gray-800/40 border border-gray-100 dark:border-gray-800">
                  <p className="text-[11px] text-gray-500">Total Listings</p>
                  <p className="mt-1 text-lg font-bold text-gray-900 dark:text-white">{dataQuality?.total_jobs ?? 0}</p>
                  <p className="text-[10px] text-gray-400 mt-0.5">Real: {dataQuality?.real_jobs ?? 0}</p>
                </div>
                <div className="p-3 rounded-xl bg-gray-50 dark:bg-gray-800/40 border border-gray-100 dark:border-gray-800">
                  <p className="text-[11px] text-gray-500">Descriptions</p>
                  <p className="mt-1 text-lg font-bold text-gray-900 dark:text-white">{dataQuality?.jobs_with_description ?? 0}</p>
                  <p className="text-[10px] text-gray-400 mt-0.5">
                    {dataQuality?.total_jobs
                      ? `${Math.round(((dataQuality.jobs_with_description) / dataQuality.total_jobs) * 100)}%`
                      : "0%"}
                  </p>
                </div>
                <div className="p-3 rounded-xl bg-gray-50 dark:bg-gray-800/40 border border-gray-100 dark:border-gray-800">
                  <p className="text-[11px] text-gray-500">Salary Data</p>
                  <p className="mt-1 text-lg font-bold text-gray-900 dark:text-white">{dataQuality?.jobs_with_salary ?? 0}</p>
                  <p className="text-[10px] text-gray-400 mt-0.5">
                    {dataQuality?.total_jobs
                      ? `${Math.round(((dataQuality.jobs_with_salary) / dataQuality.total_jobs) * 100)}%`
                      : "0%"}
                  </p>
                </div>
                <div className="p-3 rounded-xl bg-gray-50 dark:bg-gray-800/40 border border-gray-100 dark:border-gray-800">
                  <p className="text-[11px] text-gray-500">Skills Detected</p>
                  <p className="mt-1 text-lg font-bold text-gray-900 dark:text-white">{dataQuality?.jobs_with_skills ?? 0}</p>
                  <p className="text-[10px] text-gray-400 mt-0.5">
                    {dataQuality?.total_jobs
                      ? `${Math.round(((dataQuality.jobs_with_skills) / dataQuality.total_jobs) * 100)}%`
                      : "0%"}
                  </p>
                </div>
                <div className="p-3 rounded-xl bg-gray-50 dark:bg-gray-800/40 border border-gray-100 dark:border-gray-800">
                  <p className="text-[11px] text-indigo-500 font-semibold">Roles Normalized</p>
                  <p className="mt-1 text-lg font-bold text-indigo-600 dark:text-indigo-400">{dataQuality?.roles_normalized ?? 0}</p>
                  <p className="text-[10px] text-gray-400 mt-0.5">Taxonomy classified</p>
                </div>
                <div className="p-3 rounded-xl bg-gray-50 dark:bg-gray-800/40 border border-gray-100 dark:border-gray-800">
                  <p className="text-[11px] text-emerald-500 font-semibold">Locations Normalized</p>
                  <p className="mt-1 text-lg font-bold text-emerald-600 dark:text-emerald-400">{dataQuality?.locations_normalized ?? 0}</p>
                  <p className="text-[10px] text-gray-400 mt-0.5">Geocoded/Metros</p>
                </div>
              </div>
            </div>
          </div>

          {/* Main Insights Section: Top Skills & Recent Jobs */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Top Skills Demand */}
            <div className="lg:col-span-2 bg-white dark:bg-gray-900 rounded-2xl border border-gray-200/80 dark:border-gray-800 p-6 shadow-sm">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-lg font-bold text-gray-900 dark:text-white">
                    Most In-Demand Skills
                  </h2>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Calculated over {metrics?.jobs_analyzed ?? 0} listings in the selected {timePeriod.toUpperCase()} window
                  </p>
                </div>
                <Link
                  href="/skills"
                  className="text-xs font-semibold text-blue-600 dark:text-blue-400 hover:underline"
                >
                  View All Skills →
                </Link>
              </div>

              {topSkills.length === 0 ? (
                <div className="py-12 text-center text-sm text-gray-500">
                  No skills detected for the current time period.
                </div>
              ) : (
                <div className="space-y-3.5">
                  {topSkills.map((s, idx) => (
                    <div key={s.skill_id} className="flex items-center gap-4">
                      <span className="w-5 text-xs font-bold text-gray-400">
                        #{idx + 1}
                      </span>
                      <div className="flex-1">
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-sm font-semibold text-gray-900 dark:text-white">
                            {s.skill_name}
                          </span>
                          <span className="text-xs font-bold text-gray-600 dark:text-gray-300">
                            {s.percentage}% ({s.job_count} jobs)
                          </span>
                        </div>
                        <div className="w-full bg-gray-100 dark:bg-gray-800 h-2 rounded-full overflow-hidden">
                          <div
                            className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                            style={{ width: `${Math.min(s.percentage, 100)}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Quick Actions & Trends Link */}
            <div className="space-y-6">
              <div className="bg-gradient-to-br from-blue-600 to-indigo-700 rounded-2xl p-6 text-white shadow-md">
                <h3 className="text-base font-bold">Historical Trend Tracking</h3>
                <p className="mt-1 text-xs text-blue-100">
                  Compare equivalent periods (e.g. Last 30d vs Previous 30d) to identify rising vs cooling tech.
                </p>
                <div className="mt-4">
                  <Link
                    href="/trends"
                    className="inline-block px-4 py-2 rounded-xl text-xs font-bold bg-white text-blue-700 hover:bg-blue-50 transition shadow-sm"
                  >
                    Explore Skill Trends →
                  </Link>
                </div>
              </div>

              <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200/80 dark:border-gray-800 p-6 shadow-sm">
                <h3 className="text-sm font-bold text-gray-900 dark:text-white uppercase tracking-wider mb-3">
                  Skill Gap & Readiness
                </h3>
                <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">
                  Evaluate your current skill set against live target role requirements to measure Market Skill Coverage.
                </p>
                <Link
                  href="/skill-gap"
                  className="inline-block w-full text-center px-4 py-2.5 rounded-xl text-xs font-semibold text-gray-700 dark:text-gray-200 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition"
                >
                  Analyze My Skill Gap →
                </Link>
              </div>
            </div>
          </div>

          {/* Recent Ingested Jobs Table */}
          <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200/80 dark:border-gray-800 p-6 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-lg font-bold text-gray-900 dark:text-white">
                  Recent Ingested Listings
                </h2>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Latest job listings evaluated by the skill extraction engine
                </p>
              </div>
              <Link
                href="/jobs"
                className="text-xs font-semibold text-blue-600 dark:text-blue-400 hover:underline"
              >
                View All Jobs ({metrics?.jobs_analyzed ?? 0}) →
              </Link>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-gray-200 dark:border-gray-800 text-gray-400 uppercase font-semibold">
                    <th className="py-3 px-2">Job Title</th>
                    <th className="py-3 px-2">Company</th>
                    <th className="py-3 px-2">Location</th>
                    <th className="py-3 px-2">Source</th>
                    <th className="py-3 px-2">Detected Skills</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-gray-800/60">
                  {recentJobs.map((job) => (
                    <tr key={job.id} className="hover:bg-gray-50 dark:hover:bg-gray-800/40">
                      <td className="py-3 px-2 font-semibold text-gray-900 dark:text-white">
                        {job.title}
                      </td>
                      <td className="py-3 px-2 text-gray-600 dark:text-gray-300">
                        {job.company_name || "Unknown"}
                      </td>
                      <td className="py-3 px-2 text-gray-500">
                        {job.location || job.country || "Remote"}
                      </td>
                      <td className="py-3 px-2">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                          job.data_type === "real"
                            ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300"
                            : "bg-amber-50 text-amber-700 dark:bg-amber-950 dark:text-amber-300"
                        }`}>
                          {job.source}
                        </span>
                      </td>
                      <td className="py-3 px-2">
                        <div className="flex flex-wrap gap-1">
                          {job.skills.slice(0, 4).map((sk) => (
                            <span
                              key={sk.id}
                              className="px-1.5 py-0.5 rounded text-[10px] font-medium bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300"
                            >
                              {sk.name}
                            </span>
                          ))}
                          {job.skills.length > 4 && (
                            <span className="text-[10px] text-gray-400 self-center">
                              +{job.skills.length - 4}
                            </span>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
