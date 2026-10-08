"use client";

import { useEffect, useState } from "react";

interface SkillDemandItem {
  skill_id: number;
  name: string;
  category: string;
  demand_percentage: number;
  job_count: number;
  priority_score?: number;
}

interface SkillGapResult {
  target_role: string;
  jobs_analyzed: number;
  market_coverage_percentage: number;
  match_score: number;
  matched_skills: SkillDemandItem[];
  missing_high_demand: SkillDemandItem[];
  missing_nice_to_have: SkillDemandItem[];
  recommendations: string[];
  formula_description?: string;
}

export default function SkillGapPage() {
  const [userSkills, setUserSkills] = useState<string[]>([
    "Python",
    "JavaScript",
    "React",
    "Git",
    "SQL",
  ]);
  const [newSkill, setNewSkill] = useState("");
  const [targetRole, setTargetRole] = useState("Software Engineer");
  const [isDemoMode, setIsDemoMode] = useState(false);
  const [result, setResult] = useState<SkillGapResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [savingProfile, setSavingProfile] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Load user profile on mount
  useEffect(() => {
    async function loadProfile() {
      try {
        const res = await fetch("/api/profile");
        if (res.ok) {
          const profile = await res.json();
          if (profile.skills && profile.skills.length > 0) {
            setUserSkills(profile.skills);
          }
          if (profile.target_roles && profile.target_roles.length > 0) {
            setTargetRole(profile.target_roles[0]);
          }
        }
      } catch (e) {
        console.error("Failed to load profile:", e);
      }
    }
    loadProfile();
  }, []);

  // Compute skill gap whenever skills, target role, or demo mode changes
  useEffect(() => {
    let ignore = false;
    async function computeGap() {
      setLoading(true);
      try {
        const skillsParam = encodeURIComponent(userSkills.join(","));
        const roleParam = encodeURIComponent(targetRole);
        const demoParam = isDemoMode ? "&include_demo=true" : "";
        const res = await fetch(
          `/api/analytics/skill-gap?target_role=${roleParam}&skills=${skillsParam}${demoParam}`
        );
        if (res.ok && !ignore) {
          const data = await res.json();
          setResult(data);
        }
      } catch (e) {
        console.error("Error computing skill gap:", e);
      } finally {
        if (!ignore) setLoading(false);
      }
    }
    computeGap();
    return () => {
      ignore = true;
    };
  }, [userSkills, targetRole, isDemoMode]);

  const addSkill = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = newSkill.trim();
    if (trimmed && !userSkills.some((s) => s.toLowerCase() === trimmed.toLowerCase())) {
      setUserSkills([...userSkills, trimmed]);
      setNewSkill("");
    }
  };

  const removeSkill = (skillToRemove: string) => {
    setUserSkills(userSkills.filter((s) => s !== skillToRemove));
  };

  const handleSaveProfile = async () => {
    setSavingProfile(true);
    setSaveSuccess(false);
    try {
      const res = await fetch("/api/profile", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: "Developer",
          country: "India",
          target_roles: [targetRole],
          skills: userSkills,
        }),
      });
      if (res.ok) {
        setSaveSuccess(true);
        setTimeout(() => setSaveSuccess(false), 3000);
      }
    } catch (e) {
      console.error("Failed to save profile:", e);
    } finally {
      setSavingProfile(false);
    }
  };

  const coverageScore = result?.market_coverage_percentage ?? result?.match_score ?? 0;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-4 border-b border-gray-200/80 dark:border-gray-800">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-400 bg-clip-text text-transparent">
              Skill Gap & Coverage Analysis
            </h1>
            {isDemoMode && (
              <span className="px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 border border-amber-300">
                Demo Mode
              </span>
            )}
          </div>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Compare your profile skills against actual market requirements for your target role
          </p>
        </div>

        <div className="flex items-center gap-2.5">
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

          <button
            onClick={handleSaveProfile}
            disabled={savingProfile}
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 shadow-sm transition disabled:opacity-50"
          >
            {savingProfile ? "Saving..." : saveSuccess ? "Saved to Profile!" : "Save to Profile"}
          </button>
        </div>
      </div>

      {/* Target Role & Profile Skills Input Panel */}
      <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200/80 dark:border-gray-800 p-6 shadow-sm space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-gray-500 mb-1.5">
              Target Job Role
            </label>
            <select
              value={targetRole}
              onChange={(e) => setTargetRole(e.target.value)}
              className="px-3.5 py-2.5 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="Software Engineer">Software Engineer (General)</option>
              <option value="Frontend">Frontend Developer</option>
              <option value="Backend">Backend Developer</option>
              <option value="Full Stack">Full Stack Developer</option>
              <option value="DevOps">DevOps / Cloud Engineer</option>
              <option value="Data">Data Scientist / AI Engineer</option>
            </select>
          </div>

          <div className="text-xs text-gray-500 sm:text-right">
            <span>Evaluating across </span>
            <span className="font-bold text-gray-900 dark:text-white">
              {result?.jobs_analyzed ?? 0} listings
            </span>
          </div>
        </div>

        {/* Skills Tag Editor */}
        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-gray-500 mb-2">
            Your Current Skills ({userSkills.length})
          </label>
          <div className="flex flex-wrap gap-2 mb-3">
            {userSkills.map((skill) => (
              <span
                key={skill}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-blue-50 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300 border border-blue-100 dark:border-blue-900/60"
              >
                {skill}
                <button
                  type="button"
                  onClick={() => removeSkill(skill)}
                  className="hover:text-red-500 transition font-bold text-sm leading-none"
                >
                  ×
                </button>
              </span>
            ))}
          </div>

          {/* Add skill input */}
          <form onSubmit={addSkill} className="flex gap-2 max-w-md">
            <input
              type="text"
              value={newSkill}
              onChange={(e) => setNewSkill(e.target.value)}
              placeholder="Add skill (e.g. Docker, TypeScript, AWS)..."
              className="flex-1 px-3.5 py-2 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-xs focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              type="submit"
              className="px-4 py-2 rounded-xl text-xs font-bold text-white bg-gray-900 dark:bg-gray-100 dark:text-gray-900 hover:opacity-90 transition"
            >
              Add
            </button>
          </form>
        </div>
      </div>

      {/* Analysis Result Overview */}
      {result && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Market Skill Coverage Card */}
          <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200/80 dark:border-gray-800 p-8 shadow-sm flex flex-col items-center justify-center text-center">
            <p className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-2">
              Market Skill Coverage
            </p>
            <div className="relative w-36 h-36 flex items-center justify-center mb-4">
              <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                <path
                  className="text-gray-100 dark:text-gray-800"
                  strokeWidth="3.5"
                  stroke="currentColor"
                  fill="none"
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                />
                <path
                  className={`${
                    coverageScore >= 75
                      ? "text-emerald-500"
                      : coverageScore >= 50
                      ? "text-blue-500"
                      : "text-amber-500"
                  } transition-all duration-1000 ease-out`}
                  strokeDasharray={`${coverageScore}, 100`}
                  strokeWidth="3.5"
                  strokeLinecap="round"
                  stroke="currentColor"
                  fill="none"
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                />
              </svg>
              <div className="absolute text-3xl font-extrabold text-gray-900 dark:text-white">
                {loading ? "..." : `${coverageScore}%`}
              </div>
            </div>

            <span
              className={`px-3 py-1 rounded-full text-xs font-bold ${
                coverageScore >= 75
                  ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-400"
                  : coverageScore >= 50
                  ? "bg-blue-50 text-blue-700 dark:bg-blue-950/60 dark:text-blue-400"
                  : "bg-amber-50 text-amber-700 dark:bg-amber-950/60 dark:text-amber-400"
              }`}
            >
              {coverageScore >= 75
                ? "High Coverage"
                : coverageScore >= 50
                ? "Moderate Coverage"
                : "Needs Upskilling"}
            </span>

            <p className="mt-4 text-[11px] text-gray-500 dark:text-gray-400 max-w-xs leading-relaxed">
              Percentage of total market skill demand for {targetRole} covered by your verified skills.
            </p>
          </div>

          {/* Recommendations & Methodology Panel */}
          <div className="lg:col-span-2 bg-white dark:bg-gray-900 rounded-2xl border border-gray-200/80 dark:border-gray-800 p-6 shadow-sm space-y-4">
            <h2 className="text-base font-bold text-gray-900 dark:text-white">
              Targeted Career Recommendations
            </h2>
            <div className="space-y-2.5">
              {result.recommendations.map((rec, i) => (
                <div
                  key={i}
                  className="p-3.5 rounded-xl bg-blue-50/60 dark:bg-blue-950/30 border border-blue-100 dark:border-blue-900/60 text-xs text-blue-900 dark:text-blue-200 flex items-start gap-2.5"
                >
                  <span className="text-blue-600 font-bold shrink-0">→</span>
                  <span>{rec}</span>
                </div>
              ))}
            </div>

            {/* Methodology description */}
            <div className="p-3 rounded-xl bg-gray-50 dark:bg-gray-800/40 text-[11px] text-gray-500 space-y-1">
              <p className="font-semibold text-gray-700 dark:text-gray-300">Methodology & Formula:</p>
              <p>
                Coverage Score = (Sum of demand weights for skills you possess) ÷ (Sum of all role skill demands) × 100.
              </p>
              <p>
                Missing Skills Priority = Demand % × Role Relevance (1.2× if in top 5 demanded skills).
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Skills Breakdown Lists */}
      {result && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* High-Demand Missing Skills */}
          <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200/80 dark:border-gray-800 p-6 shadow-sm">
            <div className="flex items-center justify-between mb-4 pb-3 border-b border-gray-100 dark:border-gray-800">
              <div>
                <h3 className="text-sm font-bold text-gray-900 dark:text-white">
                  High-Priority Missing Skills
                </h3>
                <p className="text-xs text-gray-500">Demanded in &gt;25% of {targetRole} jobs</p>
              </div>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-50 text-rose-700 dark:bg-rose-950 dark:text-rose-300">
                {result.missing_high_demand.length} Missing
              </span>
            </div>

            {result.missing_high_demand.length === 0 ? (
              <p className="text-xs text-emerald-600 py-6 text-center font-medium">
                ✓ Outstanding: You already cover all core high-demand skills for this role!
              </p>
            ) : (
              <div className="divide-y divide-gray-100 dark:divide-gray-800">
                {result.missing_high_demand.map((sk) => (
                  <div key={sk.skill_id} className="py-3 first:pt-0 last:pb-0 flex items-center justify-between">
                    <div>
                      <p className="text-xs font-bold text-gray-900 dark:text-white">{sk.name}</p>
                      <p className="text-[10px] text-gray-400">
                        {sk.category} • Demanded in {sk.demand_percentage}% ({sk.job_count} jobs)
                      </p>
                    </div>
                    {sk.priority_score && (
                      <span className="px-2.5 py-1 rounded-lg text-[11px] font-bold bg-amber-50 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300">
                        Priority: {sk.priority_score}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Matched Skills */}
          <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200/80 dark:border-gray-800 p-6 shadow-sm">
            <div className="flex items-center justify-between mb-4 pb-3 border-b border-gray-100 dark:border-gray-800">
              <div>
                <h3 className="text-sm font-bold text-gray-900 dark:text-white">
                  Your Covered Market Skills
                </h3>
                <p className="text-xs text-gray-500">Skills you possess that match market requirements</p>
              </div>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">
                {result.matched_skills.length} Matched
              </span>
            </div>

            {result.matched_skills.length === 0 ? (
              <p className="text-xs text-gray-400 py-6 text-center">
                None of your listed skills currently match requirements for {targetRole}.
              </p>
            ) : (
              <div className="divide-y divide-gray-100 dark:divide-gray-800">
                {result.matched_skills.map((sk) => (
                  <div key={sk.skill_id} className="py-3 first:pt-0 last:pb-0 flex items-center justify-between">
                    <div>
                      <p className="text-xs font-bold text-gray-900 dark:text-white">{sk.name}</p>
                      <p className="text-[10px] text-gray-400">
                        {sk.category} • Required in {sk.demand_percentage}% of postings
                      </p>
                    </div>
                    <span className="px-2.5 py-1 rounded-lg text-[11px] font-bold bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300">
                      ✓ Covered
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
