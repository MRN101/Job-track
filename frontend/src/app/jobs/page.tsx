"use client";

import { useEffect, useState } from "react";

interface SkillInJob {
  id: number;
  name: string;
  category?: string;
  confidence: number;
}

interface Job {
  id: number;
  source: string;
  data_type: string;
  external_id?: string;
  title: string;
  company_name?: string;
  location?: string;
  country?: string;
  description?: string;
  salary_min?: number;
  salary_max?: number;
  salary_currency?: string;
  salary_period?: string;
  salary_normalized?: number;
  employment_type?: string;
  experience_level?: string;
  posted_at?: string;
  url?: string;
  skills: SkillInJob[];
}

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState("");
  const [sourceFilter, setSourceFilter] = useState("all");
  const [isDemoMode, setIsDemoMode] = useState(false);
  const [sortBy, setSortBy] = useState("newest");
  const [loading, setLoading] = useState(true);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [submittedSearch, setSubmittedSearch] = useState("");
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    let ignore = false;
    async function fetchData() {
      setLoading(true);
      try {
        const params = new URLSearchParams({
          page: page.toString(),
          page_size: pageSize.toString(),
          sort_by: sortBy,
        });
        if (submittedSearch.trim()) params.append("search", submittedSearch.trim());
        if (roleFilter.trim()) params.append("role", roleFilter.trim());
        if (sourceFilter !== "all") params.append("source", sourceFilter);
        if (isDemoMode) params.append("include_demo", "true");

        const res = await fetch(`/api/jobs?${params.toString()}`);
        if (res.ok && !ignore) {
          const data = await res.json();
          setJobs(data.jobs || []);
          setTotal(data.total || 0);
        }
      } catch (err) {
        console.error("Error fetching jobs:", err);
      } finally {
        if (!ignore) setLoading(false);
      }
    }
    fetchData();
    return () => {
      ignore = true;
    };
  }, [page, sortBy, roleFilter, sourceFilter, isDemoMode, refreshKey, pageSize, submittedSearch]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setPage(1);
    setSubmittedSearch(search);
    setRefreshKey((k) => k + 1);
  };

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-gray-200/60 dark:border-gray-800/80">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-400 bg-clip-text text-transparent">
            Job Listings Explorer
          </h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Browse collected jobs and analyze their extracted skill profiles
          </p>
        </div>
        <div className="text-xs font-semibold px-3 py-1.5 rounded-xl bg-blue-50 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300 self-start sm:self-center">
          {total} Active Opportunities
        </div>
      </div>

      {/* Filters & Search Bar */}
      <div className="bg-white dark:bg-gray-900 p-4 rounded-2xl border border-gray-200/80 dark:border-gray-800 shadow-sm flex flex-col md:flex-row items-stretch md:items-center gap-3">
        {/* Search */}
        <form onSubmit={handleSearchSubmit} className="flex-1 relative">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by title, skills, or company..."
            className="w-full pl-9 pr-4 py-2.5 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <svg
            className="w-4 h-4 absolute left-3 top-3.5 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={2}
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z"
            />
          </svg>
        </form>

        {/* Mode Switcher */}
        <div className="inline-flex p-1 rounded-xl bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-xs font-semibold shrink-0">
          <button
            type="button"
            onClick={() => {
              setIsDemoMode(false);
              setPage(1);
            }}
            className={`px-3 py-1.5 rounded-lg transition ${
              !isDemoMode ? "bg-white dark:bg-gray-900 text-blue-600 shadow-sm" : "text-gray-500"
            }`}
          >
            Real
          </button>
          <button
            type="button"
            onClick={() => {
              setIsDemoMode(true);
              setPage(1);
            }}
            className={`px-3 py-1.5 rounded-lg transition ${
              isDemoMode ? "bg-amber-500 text-white shadow-sm" : "text-gray-500"
            }`}
          >
            Demo
          </button>
        </div>

        {/* Source Filter */}
        <select
          value={sourceFilter}
          onChange={(e) => {
            setSourceFilter(e.target.value);
            setPage(1);
          }}
          className="px-3.5 py-2.5 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="all">All Sources</option>
          <option value="remotive">Remotive</option>
          <option value="adzuna">Adzuna</option>
          {isDemoMode && <option value="sample">Sample</option>}
        </select>

        {/* Role Selector */}
        <select
          value={roleFilter}
          onChange={(e) => {
            setRoleFilter(e.target.value);
            setPage(1);
          }}
          className="px-3.5 py-2.5 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Roles</option>
          <option value="Frontend">Frontend</option>
          <option value="Backend">Backend</option>
          <option value="Full Stack">Full Stack</option>
          <option value="DevOps">DevOps & Cloud</option>
          <option value="Data">Data & AI</option>
        </select>

        {/* Sort Selector */}
        <select
          value={sortBy}
          onChange={(e) => {
            setSortBy(e.target.value);
            setPage(1);
          }}
          className="px-3.5 py-2.5 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="newest">Sort: Newest First</option>
          <option value="salary">Sort: Highest Salary</option>
        </select>
      </div>

      {/* Jobs List */}
      {loading ? (
        <div className="py-20 text-center text-sm text-gray-500 animate-pulse">
          Loading job listings...
        </div>
      ) : jobs.length === 0 ? (
        <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 p-12 text-center">
          <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
            No matching jobs found
          </p>
          <p className="text-xs text-gray-500 mt-1">
            Try adjusting your search criteria or load sample data from Settings.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {jobs.map((job) => (
            <div
              key={job.id}
              className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200/80 dark:border-gray-800 p-6 shadow-sm hover:shadow-md transition cursor-pointer"
              onClick={() => setSelectedJob(job)}
            >
              <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                <div className="space-y-2 flex-1">
                  <div className="flex items-center gap-2.5 flex-wrap">
                    <h2 className="text-base font-bold text-gray-900 dark:text-white hover:text-blue-600 transition">
                      {job.title}
                    </h2>
                    {job.salary_max && (
                      <span className="px-2.5 py-0.5 rounded-lg text-xs font-bold bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300">
                        {job.salary_currency === "INR" ? "₹" : "$"}{(job.salary_max / 100000).toFixed(1)} LPA
                      </span>
                    )}
                    <span className="px-2 py-0.5 rounded-lg text-[10px] font-semibold bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 uppercase">
                      {job.source}
                    </span>
                  </div>

                  <div className="flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400 flex-wrap">
                    <span className="font-semibold text-gray-700 dark:text-gray-300">
                      {job.company_name || "Confidential"}
                    </span>
                    <span>•</span>
                    <span>{job.location || "Remote"}</span>
                    <span>•</span>
                    <span>{job.country}</span>
                    <span>•</span>
                    <span>{job.experience_level || "Not specified"}</span>
                  </div>

                  {job.description && (
                    <p className="text-xs text-gray-600 dark:text-gray-400 line-clamp-2 leading-relaxed">
                      {job.description}
                    </p>
                  )}

                  {/* Skills tags */}
                  <div className="flex items-center gap-1.5 flex-wrap pt-2">
                    {job.skills.map((s) => (
                      <span
                        key={s.id}
                        className="px-2.5 py-1 rounded-lg text-[11px] font-medium bg-blue-50 dark:bg-blue-950/40 text-blue-700 dark:text-blue-300 border border-blue-100 dark:border-blue-900/40"
                      >
                        {s.name}
                      </span>
                    ))}
                  </div>
                </div>

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedJob(job);
                  }}
                  className="shrink-0 px-4 py-2 rounded-xl text-xs font-semibold border border-gray-200 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-200 transition"
                >
                  View Full Details
                </button>
              </div>
            </div>
          ))}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between pt-4">
              <span className="text-xs text-gray-500">
                Page {page} of {totalPages}
              </span>
              <div className="flex items-center gap-2">
                <button
                  disabled={page <= 1}
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  className="px-3 py-1.5 rounded-lg border border-gray-200 dark:border-gray-800 text-xs font-semibold disabled:opacity-40"
                >
                  Previous
                </button>
                <button
                  disabled={page >= totalPages}
                  onClick={() => setPage((p) => p + 1)}
                  className="px-3 py-1.5 rounded-lg border border-gray-200 dark:border-gray-800 text-xs font-semibold disabled:opacity-40"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Detail Modal */}
      {selectedJob && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white dark:bg-gray-900 rounded-3xl max-w-2xl w-full max-h-[85vh] overflow-y-auto p-6 md:p-8 shadow-2xl border border-gray-200 dark:border-gray-800 space-y-6">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-xl font-extrabold text-gray-900 dark:text-white">
                  {selectedJob.title}
                </h3>
                <p className="text-sm font-semibold text-blue-600 dark:text-blue-400 mt-0.5">
                  {selectedJob.company_name} • {selectedJob.location}
                </p>
              </div>
              <button
                onClick={() => setSelectedJob(null)}
                className="p-1.5 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500 transition"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Quick Metadata Pill Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="p-3 rounded-xl bg-gray-50 dark:bg-gray-800/60">
                <p className="text-gray-400 text-[10px] uppercase font-bold">Salary Range</p>
                <p className="font-bold text-emerald-600 dark:text-emerald-400 mt-0.5">
                  {selectedJob.salary_max
                    ? `${selectedJob.salary_currency === "INR" ? "₹" : "$"}${(
                        selectedJob.salary_max / 100000
                      ).toFixed(1)} LPA`
                    : "Competitive"}
                </p>
              </div>
              <div className="p-3 rounded-xl bg-gray-50 dark:bg-gray-800/60">
                <p className="text-gray-400 text-[10px] uppercase font-bold">Experience</p>
                <p className="font-bold text-gray-800 dark:text-gray-200 mt-0.5">
                  {selectedJob.experience_level || "Any"}
                </p>
              </div>
              <div className="p-3 rounded-xl bg-gray-50 dark:bg-gray-800/60">
                <p className="text-gray-400 text-[10px] uppercase font-bold">Work Type</p>
                <p className="font-bold text-gray-800 dark:text-gray-200 mt-0.5">
                  {selectedJob.employment_type || "Full Time"}
                </p>
              </div>
              <div className="p-3 rounded-xl bg-gray-50 dark:bg-gray-800/60">
                <p className="text-gray-400 text-[10px] uppercase font-bold">Source</p>
                <p className="font-bold text-gray-800 dark:text-gray-200 mt-0.5 uppercase">
                  {selectedJob.source}
                </p>
              </div>
            </div>

            {/* Extracted Skills */}
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-2">
                Extracted Required Skills ({selectedJob.skills.length})
              </h4>
              <div className="flex items-center gap-2 flex-wrap">
                {selectedJob.skills.map((s) => (
                  <span
                    key={s.id}
                    className="px-3 py-1 rounded-xl text-xs font-semibold bg-blue-50 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300 border border-blue-100 dark:border-blue-900/60"
                  >
                    {s.name}
                    {s.category && (
                      <span className="ml-1.5 opacity-60 text-[10px]">({s.category})</span>
                    )}
                  </span>
                ))}
              </div>
            </div>

            {/* Description */}
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-2">
                Job Description
              </h4>
              <div className="p-4 rounded-2xl bg-gray-50 dark:bg-gray-800/40 text-xs text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-line">
                {selectedJob.description || "No description provided."}
              </div>
            </div>

            {/* Action buttons */}
            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={() => setSelectedJob(null)}
                className="px-4 py-2 rounded-xl text-xs font-semibold border border-gray-200 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800 transition"
              >
                Close
              </button>
              {selectedJob.url && (
                <a
                  href={selectedJob.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-5 py-2 rounded-xl text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 shadow-sm transition"
                >
                  Apply on Job Site →
                </a>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
