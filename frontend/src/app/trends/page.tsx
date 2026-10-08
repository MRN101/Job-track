"use client";

import { useEffect, useState } from "react";

interface TrendSkill {
  skill_id: number;
  skill_name: string;
  category?: string;
  current_percentage: number;
  previous_percentage?: number;
  change_pp?: number;
  trend_direction?: "up" | "down" | "stable";
}

interface TrendsData {
  emerging: TrendSkill[];
  declining: TrendSkill[];
  period: string;
  has_sufficient_data: boolean;
}

export default function TrendsPage() {
  const [trends, setTrends] = useState<TrendsData | null>(null);
  const [period, setPeriod] = useState("30d");
  const [loading, setLoading] = useState(true);
  const [snapshotting, setSnapshotting] = useState(false);

  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    let ignore = false;
    async function fetchData() {
      try {
        const res = await fetch(`/api/analytics/trends?period=${period}`);
        if (res.ok && !ignore) {
          const data = await res.json();
          setTrends(data);
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
  }, [period, refreshKey]);

  const handleTakeSnapshot = async () => {
    setSnapshotting(true);
    try {
      const res = await fetch("/api/analytics/run-snapshot", {
        method: "POST",
      });
      if (res.ok) {
        setRefreshKey((k) => k + 1);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setSnapshotting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-gray-200/60 dark:border-gray-800/80">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-400 bg-clip-text text-transparent">
            Skill Demand Trends
          </h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Track emerging technologies gaining adoption and declining frameworks
          </p>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={period}
            onChange={(e) => setPeriod(e.target.value)}
            className="px-3.5 py-2 rounded-xl bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 text-xs font-medium shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 90 Days</option>
            <option value="6m">Last 6 Months</option>
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
            {snapshotting ? "Saving..." : "Take Trend Snapshot"}
          </button>
        </div>
      </div>

      {loading ? (
        <div className="py-20 text-center text-sm text-gray-500 animate-pulse">
          Calculating trends across historical runs...
        </div>
      ) : !trends?.has_sufficient_data ? (
        <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 p-12 text-center space-y-3">
          <div className="mx-auto w-12 h-12 rounded-full bg-blue-50 dark:bg-blue-950/60 flex items-center justify-center text-blue-600">
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 18 9 11.25l4.306 4.306a11.95 11.95 0 0 1 5.814-5.518l2.74-1.22m0 0-5.94-2.281m5.94 2.28-2.28 5.941" />
            </svg>
          </div>
          <h3 className="text-base font-bold text-gray-900 dark:text-white">
            Historical Data Gathering in Progress
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400 max-w-md mx-auto leading-relaxed">
            Trend comparison requires at least 2 historical analysis runs. Click the button below to take a snapshot now.
          </p>
          <button
            onClick={handleTakeSnapshot}
            className="px-4 py-2 rounded-xl text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 transition shadow-sm"
          >
            Create Historical Snapshot
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Emerging Skills */}
          <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200/80 dark:border-gray-800 p-6 shadow-sm">
            <div className="flex items-center gap-2 mb-4">
              <div className="p-2 rounded-lg bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 18 9 11.25l4.306 4.306a11.95 11.95 0 0 1 5.814-5.518l2.74-1.22" />
                </svg>
              </div>
              <div>
                <h2 className="text-base font-bold text-gray-900 dark:text-white">
                  Emerging Skills (Growing Demand)
                </h2>
                <p className="text-xs text-gray-500">Skills showing highest positive percentage gain</p>
              </div>
            </div>

            {trends.emerging.length === 0 ? (
              <p className="text-xs text-gray-400 py-6 text-center">
                Demand across tracked skills is currently stable.
              </p>
            ) : (
              <div className="divide-y divide-gray-100 dark:divide-gray-800">
                {trends.emerging.map((s) => (
                  <div key={s.skill_id} className="py-3 first:pt-0 last:pb-0 flex items-center justify-between">
                    <div>
                      <p className="text-xs font-bold text-gray-900 dark:text-white">
                        {s.skill_name}
                      </p>
                      <p className="text-[10px] text-gray-400">
                        {s.category} • Current {s.current_percentage}%
                      </p>
                    </div>
                    <span className="px-2.5 py-1 rounded-lg text-xs font-bold bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
                      ▲ +{s.change_pp} pp
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Declining / Shifting Skills */}
          <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200/80 dark:border-gray-800 p-6 shadow-sm">
            <div className="flex items-center gap-2 mb-4">
              <div className="p-2 rounded-lg bg-rose-50 dark:bg-rose-950/60 text-rose-600">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 6 9 12.75l4.306-4.306a11.95 11.95 0 0 1 5.814 5.518l2.74 1.22" />
                </svg>
              </div>
              <div>
                <h2 className="text-base font-bold text-gray-900 dark:text-white">
                  Declining / Stabilizing Demand
                </h2>
                <p className="text-xs text-gray-500">Skills losing share compared to prior snapshot</p>
              </div>
            </div>

            {trends.declining.length === 0 ? (
              <p className="text-xs text-gray-400 py-6 text-center">
                No notable demand decline detected in the current period.
              </p>
            ) : (
              <div className="divide-y divide-gray-100 dark:divide-gray-800">
                {trends.declining.map((s) => (
                  <div key={s.skill_id} className="py-3 first:pt-0 last:pb-0 flex items-center justify-between">
                    <div>
                      <p className="text-xs font-bold text-gray-900 dark:text-white">
                        {s.skill_name}
                      </p>
                      <p className="text-[10px] text-gray-400">
                        {s.category} • Current {s.current_percentage}%
                      </p>
                    </div>
                    <span className="px-2.5 py-1 rounded-lg text-xs font-bold bg-rose-50 dark:bg-rose-950/60 text-rose-600 dark:text-rose-400 flex items-center gap-1">
                      ▼ {s.change_pp} pp
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
