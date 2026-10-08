"use client";

import { useEffect, useState } from "react";
import Sidebar from "@/components/Sidebar";

interface CollectionRunItem {
  id: number;
  source: string;
  status: string;
  started_at: string;
  completed_at?: string;
  jobs_retrieved: number;
  new_jobs: number;
  updated_jobs: number;
  duplicates: number;
  failed_jobs: number;
  skills_extracted: number;
  error_message?: string;
}

interface SchedulerStatus {
  running: boolean;
  interval: string;
  last_run: string | null;
  last_status: string;
  next_run: string | null;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export default function CollectionHistoryPage() {
  const [runs, setRuns] = useState<CollectionRunItem[]>([]);
  const [scheduler, setScheduler] = useState<SchedulerStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [triggering, setTriggering] = useState(false);
  const [triggerMsg, setTriggerMsg] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [historyRes, schedRes] = await Promise.all([
        fetch(`${API_BASE}/api/analytics/collections/history`),
        fetch(`${API_BASE}/api/analytics/scheduler/status`),
      ]);

      if (historyRes.ok) {
        const historyData = await historyRes.json();
        setRuns(historyData);
      }
      if (schedRes.ok) {
        const schedData = await schedRes.json();
        setScheduler(schedData);
      }
    } catch (err) {
      console.error("Failed to load collection history:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleTriggerNow = async () => {
    try {
      setTriggering(true);
      setTriggerMsg(null);
      const res = await fetch(`${API_BASE}/api/analytics/scheduler/trigger`, {
        method: "POST",
      });
      if (res.ok) {
        setTriggerMsg("Collection pipeline initiated in background! Refresh in a few seconds.");
        setTimeout(fetchData, 4000);
      } else {
        setTriggerMsg("Failed to initiate collection.");
      }
    } catch (e: any) {
      setTriggerMsg("Error triggering collection: " + e.message);
    } finally {
      setTriggering(false);
    }
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 font-sans">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-y-auto">
        <header className="px-8 py-6 border-b border-slate-800/80 bg-slate-900/40 backdrop-blur-md flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-3">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
              Collection Monitoring & History
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Audit log of scheduled and manual real job-market ingestion runs
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={fetchData}
              className="px-3.5 py-2 text-xs font-medium rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700 transition"
            >
              Refresh
            </button>
            <button
              onClick={handleTriggerNow}
              disabled={triggering}
              className="px-4 py-2 text-xs font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-600/20 transition disabled:opacity-50"
            >
              {triggering ? "Starting..." : "Run Collection Now"}
            </button>
          </div>
        </header>

        <main className="p-8 space-y-6 max-w-6xl">
          {triggerMsg && (
            <div className="p-4 rounded-xl bg-indigo-950/60 border border-indigo-800 text-indigo-200 text-xs flex items-center justify-between">
              <span>{triggerMsg}</span>
              <button onClick={() => setTriggerMsg(null)} className="text-indigo-400 hover:text-white">✕</button>
            </div>
          )}

          {/* Scheduler Status Card */}
          {scheduler && (
            <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <p className="text-xs font-medium text-slate-400">Scheduler State</p>
                <div className="flex items-center gap-2 mt-1">
                  <span className={`w-2 h-2 rounded-full ${scheduler.running ? "bg-emerald-400" : "bg-amber-400"}`} />
                  <p className="text-sm font-semibold text-slate-100">
                    {scheduler.running ? "Active Background" : "Paused / Manual"}
                  </p>
                </div>
              </div>
              <div>
                <p className="text-xs font-medium text-slate-400">Schedule Cadence</p>
                <p className="text-sm font-semibold text-slate-100 mt-1 capitalize">{scheduler.interval}</p>
              </div>
              <div>
                <p className="text-xs font-medium text-slate-400">Last Pipeline Status</p>
                <p className="text-sm font-semibold text-slate-100 mt-1 capitalize">{scheduler.last_status}</p>
              </div>
              <div>
                <p className="text-xs font-medium text-slate-400">Next Scheduled Execution</p>
                <p className="text-xs font-semibold text-slate-300 mt-1">
                  {scheduler.next_run ? new Date(scheduler.next_run).toLocaleString() : "Manual trigger only"}
                </p>
              </div>
            </div>
          )}

          {/* Collection Run History List */}
          <div className="space-y-4">
            <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
              Execution Logs ({runs.length} runs recorded)
            </h2>

            {loading ? (
              <div className="py-16 text-center text-slate-500 text-sm">Loading collection history...</div>
            ) : runs.length === 0 ? (
              <div className="p-8 rounded-2xl bg-slate-900/40 border border-slate-800 text-center">
                <p className="text-sm text-slate-400">No collection executions recorded yet.</p>
                <p className="text-xs text-slate-500 mt-1">
                  Click &apos;Run Collection Now&apos; above or configure daily scheduled collection.
                </p>
              </div>
            ) : (
              runs.map((run) => {
                const isCompleted = run.status === "completed";
                const isPartial = run.status === "partial";
                const isFailed = run.status === "failed";

                return (
                  <div
                    key={run.id}
                    className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 hover:border-slate-700/80 transition"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <span className="text-sm font-bold text-white capitalize">{run.source}</span>
                        <span
                          className={`px-2.5 py-0.5 text-xs font-semibold rounded-full ${
                            isCompleted
                              ? "bg-emerald-950 text-emerald-400 border border-emerald-800/50"
                              : isPartial
                              ? "bg-amber-950 text-amber-400 border border-amber-800/50"
                              : isFailed
                              ? "bg-rose-950 text-rose-400 border border-rose-800/50"
                              : "bg-blue-950 text-blue-400 border border-blue-800/50"
                          }`}
                        >
                          {run.status.toUpperCase()}
                        </span>
                      </div>
                      <span className="text-xs text-slate-400">
                        {new Date(run.started_at).toLocaleString()}
                      </span>
                    </div>

                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-2 pt-2 border-t border-slate-800/50">
                      <div>
                        <span className="text-xs text-slate-500">Retrieved</span>
                        <p className="text-sm font-semibold text-slate-200">{run.jobs_retrieved.toLocaleString()}</p>
                      </div>
                      <div>
                        <span className="text-xs text-emerald-500 font-medium">New Ingested</span>
                        <p className="text-sm font-semibold text-emerald-400">{run.new_jobs.toLocaleString()}</p>
                      </div>
                      <div>
                        <span className="text-xs text-slate-500">Duplicates Deduplicated</span>
                        <p className="text-sm font-semibold text-slate-300">{run.duplicates.toLocaleString()}</p>
                      </div>
                      <div>
                        <span className="text-xs text-rose-500 font-medium">Errors / Failed</span>
                        <p className="text-sm font-semibold text-rose-400">{run.failed_jobs}</p>
                      </div>
                    </div>

                    {run.error_message && (
                      <div className="mt-3 p-3 rounded-lg bg-rose-950/40 border border-rose-900/40 text-rose-300 text-xs">
                        <span className="font-semibold">Reason: </span>
                        {run.error_message}
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
