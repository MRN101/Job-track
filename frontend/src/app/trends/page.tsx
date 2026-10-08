"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface TrendSkill {
  skill_id: number;
  skill_name: string;
  category?: string;
  current_percentage: number;
  previous_percentage?: number;
  change_pp?: number;
  current_job_count: number;
  previous_job_count: number;
  trend_direction?: "up" | "down" | "stable";
}

interface CandidateSkill {
  id: number;
  name: string;
  normalized_name?: string;
  job_count: number;
  occurrences: number;
  confidence: number;
  status: string;
  first_seen_at?: string;
  last_seen_at?: string;
}

interface AlertItem {
  type: string;
  title: string;
  message: string;
  severity: string;
  timestamp: string;
  data?: any;
}

interface TrendsData {
  emerging: TrendSkill[];
  declining: TrendSkill[];
  period: string;
  has_sufficient_data: boolean;
  current_period_label?: string;
  previous_period_label?: string;
  current_jobs_count: number;
  previous_jobs_count: number;
  message?: string;
}

export default function TrendsPage() {
  const [trends, setTrends] = useState<TrendsData | null>(null);
  const [candidateSkills, setCandidateSkills] = useState<CandidateSkill[]>([]);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [period, setPeriod] = useState("30d");
  const [isDemoMode, setIsDemoMode] = useState(false);
  const [role, setRole] = useState("all");
  const [loading, setLoading] = useState(true);
  const [snapshotting, setSnapshotting] = useState(false);
  const [snapshotMessage, setSnapshotMessage] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    let ignore = false;
    async function fetchData() {
      setLoading(true);
      try {
        const demoParam = isDemoMode ? "&include_demo=true" : "";
        const roleParam = role !== "all" ? `&role=${encodeURIComponent(role)}` : "";
        const [trendsRes, candRes, alertRes] = await Promise.all([
          fetch(`/api/analytics/trends?period=${period}${demoParam}${roleParam}`),
          fetch(`/api/analytics/candidate-skills?status=candidate&limit=10`),
          fetch(`/api/analytics/alerts?growth_threshold=2.0`),
        ]);

        if (trendsRes.ok && !ignore) {
          const data = await trendsRes.json();
          setTrends(data);
        }
        if (candRes.ok && !ignore) {
          const cData = await candRes.json();
          setCandidateSkills(cData);
        }
        if (alertRes.ok && !ignore) {
          const aData = await alertRes.json();
          setAlerts(aData);
        }
      } catch (e) {
        console.error("Error fetching trends:", e);
      } finally {
        if (!ignore) setLoading(false);
      }
    }
    fetchData();
    return () => {
      ignore = true;
    };
  }, [period, role, isDemoMode, refreshKey]);

  const handleTakeSnapshot = async () => {
    setSnapshotting(true);
    setSnapshotMessage(null);
    try {
      const demoParam = isDemoMode ? "?include_demo=true" : "";
      const res = await fetch(`/api/analytics/run-snapshot${demoParam}`, {
        method: "POST",
      });
      if (res.ok) {
        const data = await res.json();
        setSnapshotMessage(`Analysis snapshot #${data.analysis_run_id} saved (${data.jobs_analyzed} jobs analyzed).`);
        setRefreshKey((k) => k + 1);
        setTimeout(() => setSnapshotMessage(null), 4000);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setSnapshotting(false);
    }
  };

  const handleApproveCandidate = async (candId: number) => {
    try {
      const res = await fetch(`/api/analytics/candidate-skills/${candId}/approve`, { method: "POST" });
      if (res.ok) {
        setCandidateSkills((prev) => prev.filter((c) => c.id !== candId));
        setSnapshotMessage("Skill approved into canonical taxonomy!");
        setTimeout(() => setSnapshotMessage(null), 3000);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleRejectCandidate = async (candId: number) => {
    try {
      const res = await fetch(`/api/analytics/candidate-skills/${candId}/reject`, { method: "POST" });
      if (res.ok) {
        setCandidateSkills((prev) => prev.filter((c) => c.id !== candId));
      }
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-4 border-b border-gray-200/80 dark:border-gray-800">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-400 bg-clip-text text-transparent">
              Skill Demand Trends
            </h1>
            {isDemoMode && (
              <span className="px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 border border-amber-300">
                Demo Mode
              </span>
            )}
          </div>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Compare verified historical periods to evaluate rising technologies and cooling frameworks
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          {/* Real vs Demo toggle */}
          <div className="inline-flex p-1 rounded-xl bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-xs font-semibold">
            <button
              onClick={() => setIsDemoMode(false)}
              className={`px-3 py-1.5 rounded-lg transition ${
                !isDemoMode ? "bg-white dark:bg-gray-900 text-blue-600 shadow-sm" : "text-gray-500"
              }`}
            >
              Real Data
            </button>
            <button
              onClick={() => setIsDemoMode(true)}
              className={`px-3 py-1.5 rounded-lg transition ${
                isDemoMode ? "bg-amber-500 text-white shadow-sm" : "text-gray-500"
              }`}
            >
              Demo Dataset
            </button>
          </div>

          <select
            value={role}
            onChange={(e) => setRole(e.target.value)}
            className="px-3.5 py-2 rounded-xl bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 text-xs font-medium shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Roles</option>
            <option value="Software Engineer">Software Engineer</option>
            <option value="Frontend">Frontend</option>
            <option value="Backend">Backend</option>
            <option value="Full Stack">Full Stack</option>
            <option value="DevOps">DevOps</option>
          </select>

          <select
            value={period}
            onChange={(e) => setPeriod(e.target.value)}
            className="px-3.5 py-2 rounded-xl bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 text-xs font-medium shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="7d">Last 7 Days vs Prior 7 Days</option>
            <option value="30d">Last 30 Days vs Prior 30 Days</option>
            <option value="90d">Last 90 Days vs Prior 90 Days</option>
            <option value="6m">Last 6 Months vs Prior 6 Months</option>
          </select>

          <button
            onClick={handleTakeSnapshot}
            disabled={snapshotting}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 shadow-sm transition disabled:opacity-50"
          >
            <svg
              className={`w-3.5 h-3.5 ${snapshotting ? "animate-spin" : ""}`}
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={2}
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5m-13.5-9L12 3m0 0 4.5 4.5M12 3v13.5" />
            </svg>
            {snapshotting ? "Saving..." : "Record Snapshot"}
          </button>
        </div>
      </div>

      {snapshotMessage && (
        <div className="p-3.5 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-200 text-xs font-medium">
          {snapshotMessage}
        </div>
      )}

      {/* Personal Market Intelligence Alerts (Phase 31) */}
      {alerts && alerts.length > 0 && (
        <div className="bg-indigo-950/40 border border-indigo-900/60 rounded-2xl p-5 space-y-3">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-indigo-400 animate-ping" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-indigo-300">
              Personal Intelligence Alerts ({alerts.length})
            </h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {alerts.slice(0, 3).map((a, idx) => (
              <div key={idx} className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-xs">
                <span className="font-bold text-slate-100 block">{a.title}</span>
                <p className="text-slate-400 text-[11px] mt-1">{a.message}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Comparison Methodology Card */}
      <div className="p-4 rounded-2xl bg-blue-50/70 dark:bg-blue-950/30 border border-blue-200/80 dark:border-blue-900/60 text-xs text-blue-950 dark:text-blue-200 flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div className="space-y-1">
          <p className="font-bold text-sm text-blue-900 dark:text-blue-100">
            Methodology: Equivalent Real Window Comparison
          </p>
          <p className="text-gray-600 dark:text-gray-400">
            {trends?.current_period_label || "Current Period"} ({trends?.current_jobs_count ?? 0} jobs) compared directly with {trends?.previous_period_label || "Previous Equivalent Period"} ({trends?.previous_jobs_count ?? 0} jobs).
          </p>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <span className="px-2.5 py-1 rounded-lg bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 font-semibold border border-blue-100 dark:border-blue-900">
            Metric: Percentage Points (pp)
          </span>
        </div>
      </div>

      {loading ? (
        <div className="py-20 text-center text-sm text-gray-500 animate-pulse">
          Computing period-over-period statistics...
        </div>
      ) : !trends?.has_sufficient_data ? (
        <div className="bg-white dark:bg-gray-900 rounded-3xl border border-gray-200 dark:border-gray-800 p-12 text-center space-y-4 shadow-sm max-w-2xl mx-auto my-6">
          <div className="mx-auto w-14 h-14 rounded-2xl bg-amber-50 dark:bg-amber-950/60 flex items-center justify-center text-amber-600">
            <svg className="w-7 h-7" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z" />
            </svg>
          </div>
          <div>
            <h3 className="text-lg font-bold text-gray-900 dark:text-white">
              Not Enough Historical Data
            </h3>
            <p className="text-xs text-gray-500 dark:text-gray-400 max-w-md mx-auto leading-relaxed mt-1">
              {trends?.message || "Trend analysis requires genuine historical job listings across at least two distinct time windows (at least 2 jobs in each). JobPulse never manufactures simulated variance."}
            </p>
          </div>
          <div className="flex justify-center gap-3 pt-2">
            <Link
              href="/"
              className="px-4 py-2 rounded-xl text-xs font-semibold bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-200 transition"
            >
              ← Back to Dashboard
            </Link>
            {!isDemoMode && (
              <button
                onClick={() => setIsDemoMode(true)}
                className="px-4 py-2 rounded-xl text-xs font-semibold bg-amber-500 hover:bg-amber-600 text-white transition shadow-sm"
              >
                View Sample Demo Trends
              </button>
            )}
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Emerging Skills */}
          <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200/80 dark:border-gray-800 p-6 shadow-sm">
            <div className="flex items-center gap-2.5 mb-5 pb-3 border-b border-gray-100 dark:border-gray-800">
              <div className="p-2 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600">
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 18 9 11.25l4.306 4.306a11.95 11.95 0 0 1 5.814-5.518l2.74-1.22" />
                </svg>
              </div>
              <div>
                <h2 className="text-base font-bold text-gray-900 dark:text-white">
                  Emerging Skills (Demand Surge)
                </h2>
                <p className="text-xs text-gray-500">Skills with higher market share than previous period</p>
              </div>
            </div>

            {trends.emerging.length === 0 ? (
              <p className="text-xs text-gray-400 py-8 text-center">
                No skills met the minimum threshold for emerging growth in this window.
              </p>
            ) : (
              <div className="divide-y divide-gray-100 dark:divide-gray-800">
                {trends.emerging.map((s) => (
                  <div key={s.skill_id} className="py-3.5 first:pt-0 last:pb-0 flex items-center justify-between gap-4">
                    <div>
                      <p className="text-sm font-bold text-gray-900 dark:text-white">
                        {s.skill_name}
                      </p>
                      <p className="text-[11px] text-gray-500 dark:text-gray-400 mt-0.5">
                        Current: <span className="font-semibold">{s.current_percentage}%</span> ({s.current_job_count} jobs) • Prev: {s.previous_percentage}% ({s.previous_job_count} jobs)
                      </p>
                    </div>
                    <span className="px-3 py-1.5 rounded-xl text-xs font-bold bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-400 flex items-center gap-1 shrink-0">
                      ▲ +{s.change_pp} pp
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Declining / Cooling Skills */}
          <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200/80 dark:border-gray-800 p-6 shadow-sm">
            <div className="flex items-center gap-2.5 mb-5 pb-3 border-b border-gray-100 dark:border-gray-800">
              <div className="p-2 rounded-xl bg-rose-50 dark:bg-rose-950/60 text-rose-600">
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 6 9 12.75l4.306-4.306a11.95 11.95 0 0 1 5.814 5.518l2.74 1.22" />
                </svg>
              </div>
              <div>
                <h2 className="text-base font-bold text-gray-900 dark:text-white">
                  Declining / Cooling Demand
                </h2>
                <p className="text-xs text-gray-500">Skills losing market share relative to prior equivalent period</p>
              </div>
            </div>

            {trends.declining.length === 0 ? (
              <p className="text-xs text-gray-400 py-8 text-center">
                No skills showed significant market share decline in this window.
              </p>
            ) : (
              <div className="divide-y divide-gray-100 dark:divide-gray-800">
                {trends.declining.map((s) => (
                  <div key={s.skill_id} className="py-3.5 first:pt-0 last:pb-0 flex items-center justify-between gap-4">
                    <div>
                      <p className="text-sm font-bold text-gray-900 dark:text-white">
                        {s.skill_name}
                      </p>
                      <p className="text-[11px] text-gray-500 dark:text-gray-400 mt-0.5">
                        Current: <span className="font-semibold">{s.current_percentage}%</span> ({s.current_job_count} jobs) • Prev: {s.previous_percentage}% ({s.previous_job_count} jobs)
                      </p>
                    </div>
                    <span className="px-3 py-1.5 rounded-xl text-xs font-bold bg-rose-50 dark:bg-rose-950/60 text-rose-700 dark:text-rose-400 flex items-center gap-1 shrink-0">
                      ▼ {s.change_pp} pp
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Candidate Emerging Tech Radar (Phase 15, 16, 17) */}
      <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200/80 dark:border-gray-800 p-6 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-gray-900 dark:text-white flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-indigo-500" />
              Candidate Emerging Tech Radar
            </h2>
            <p className="text-xs text-gray-500">
              Uncatalogued technical phrases detected by NLP heuristics in live job descriptions. Approve to promote into canonical taxonomy.
            </p>
          </div>
          <span className="text-xs text-slate-500 font-medium">
            {candidateSkills.length} candidates tracked
          </span>
        </div>

        {candidateSkills.length === 0 ? (
          <p className="text-xs text-gray-400 py-6 text-center">
            No uncatalogued candidates detected yet. Run job collection to discover new tools.
          </p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {candidateSkills.map((cand) => (
              <div
                key={cand.id}
                className="p-4 rounded-xl bg-gray-50 dark:bg-gray-800/50 border border-gray-200/60 dark:border-gray-800 flex items-center justify-between gap-3"
              >
                <div>
                  <p className="text-sm font-bold text-gray-900 dark:text-white">{cand.name}</p>
                  <p className="text-[11px] text-gray-500 mt-0.5">
                    Found in <span className="font-semibold text-indigo-600 dark:text-indigo-400">{cand.job_count} jobs</span> • Conf: {Math.round(cand.confidence * 100)}%
                  </p>
                </div>
                <div className="flex items-center gap-1.5 shrink-0">
                  <button
                    onClick={() => handleApproveCandidate(cand.id)}
                    className="px-2.5 py-1 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white transition"
                    title="Promote to canonical taxonomy"
                  >
                    Approve
                  </button>
                  <button
                    onClick={() => handleRejectCandidate(cand.id)}
                    className="px-2 py-1 rounded-lg text-xs font-semibold bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-300 transition"
                    title="Reject candidate"
                  >
                    ✕
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
