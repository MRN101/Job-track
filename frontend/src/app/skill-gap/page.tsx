"use client";

import { useEffect, useState } from "react";

interface SkillDemandItem {
  skill_id: number;
  name: string;
  category: string;
  demand_percentage: number;
  job_count: number;
}

interface SkillGapResult {
  target_role: string;
  jobs_analyzed: number;
  match_score: number;
  matched_skills: SkillDemandItem[];
  missing_high_demand: SkillDemandItem[];
  missing_nice_to_have: SkillDemandItem[];
  recommendations: string[];
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

  // Compute skill gap whenever skills or target role changes
  useEffect(() => {
    let ignore = false;
    async function computeGap() {
      try {
        const skillsParam = encodeURIComponent(userSkills.join(","));
        const roleParam = encodeURIComponent(targetRole);
        const res = await fetch(
          `/api/analytics/skill-gap?target_role=${roleParam}&skills=${skillsParam}`
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
  }, [userSkills, targetRole]);

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

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-gray-200/60 dark:border-gray-800/80">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-400 bg-clip-text text-transparent">
            Skill Gap Analysis
          </h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Compare your profile against actual market demand for your target role
          </p>
        </div>

        <button
          onClick={handleSaveProfile}
          disabled={savingProfile}
          className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 shadow-sm transition disabled:opacity-50 self-start sm:self-center"
        >
          {savingProfile ? "Saving..." : saveSuccess ? "Saved to Profile!" : "Save to Profile"}
        </button>
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
            <span>Analyzing against </span>
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
          {/* Match Score Card */}
          <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200/80 dark:border-gray-800 p-8 shadow-sm flex flex-col items-center justify-center text-center">
            <p className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-3">
              Role Match Score
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
                    result.match_score >= 75
                      ? "text-emerald-500"
                      : result.match_score >= 50
                      ? "text-blue-500"
                      : "text-amber-500"
                  } transition-all duration-1000 ease-out`}
                  strokeDasharray={`${result.match_score}, 100`}
                  strokeWidth="3.5"
                  strokeLinecap="round"
                  stroke="currentColor"
                  fill="none"
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                />
              </svg>
              <div className="absolute text-3xl font-extrabold text-gray-900 dark:text-white">
                {loading ? "..." : `${result.match_score}%`}
              </div>
            </div>

            <span
              className={`px-3 py-1 rounded-full text-xs font-bold ${
                result.match_score >= 75
                  ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-400"
                  : result.match_score >= 50
                  ? "bg-blue-50 text-blue-700 dark:bg-blue-950/60 dark:text-blue-400"
                  : "bg-amber-50 text-amber-700 dark:bg-amber-950/60 dark:text-amber-400"
              }`}
            >
              {result.match_score >= 75
                ? "Strong Profile Match"
                : result.match_score >= 50
                ? "Moderate Readiness"
                : "Needs Up-skilling"}
            </span>

            {/* Quick Stats */}
            <div className="grid grid-cols-2 gap-4 w-full mt-6 pt-6 border-t border-gray-100 dark:border-gray-800 text-xs">
              <div>
                <p className="text-gray-400 text-[10px] uppercase font-bold">Matched</p>
                <p className="font-bold text-gray-900 dark:text-white mt-0.5">
                  {result.matched_skills.length} Skills
                </p>
              </div>
              <div>
                <p className="text-gray-400 text-[10px] uppercase font-bold">Missing Core</p>
                <p className="font-bold text-rose-600 dark:text-rose-400 mt-0.5">
                  {result.missing_high_demand.length} Skills
                </p>
              </div>
            </div>
          </div>

          {/* Breakdown Lists (2 cols) */}
          <div className="lg:col-span-2 space-y-6">
            {/* Missing High-Demand Skills */}
            <div className="bg-white dark:bg-gray-900 rounded-2xl border border-rose-200/60 dark:border-rose-950/40 p-6 shadow-sm">
              <div className="flex items-center gap-2 mb-3">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span>
                <h3 className="text-sm font-bold text-gray-900 dark:text-white">
                  High-Priority Missing Skills (In High Market Demand)
                </h3>
              </div>
              {result.missing_high_demand.length === 0 ? (
                <p className="text-xs text-gray-500">
                  Great job! You have covered all top high-demand skills for this role.
                </p>
              ) : (
                <div className="flex flex-wrap gap-2">
                  {result.missing_high_demand.map((s) => (
                    <div
                      key={s.skill_id}
                      className="px-3 py-1.5 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200/80 dark:border-rose-900/60 text-xs font-semibold text-rose-800 dark:text-rose-300 flex items-center gap-2"
                    >
                      <span>{s.name}</span>
                      <span className="px-1.5 py-0.2 rounded-md bg-rose-200/70 dark:bg-rose-900 text-[10px] font-bold">
                        {s.demand_percentage}% demand
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Matched Skills */}
            <div className="bg-white dark:bg-gray-900 rounded-2xl border border-emerald-200/60 dark:border-emerald-950/40 p-6 shadow-sm">
              <div className="flex items-center gap-2 mb-3">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
                <h3 className="text-sm font-bold text-gray-900 dark:text-white">
                  Skills You Have (Verified In Demand)
                </h3>
              </div>
              <div className="flex flex-wrap gap-2">
                {result.matched_skills.map((s) => (
                  <div
                    key={s.skill_id}
                    className="px-3 py-1.5 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200/80 dark:border-emerald-900/60 text-xs font-semibold text-emerald-800 dark:text-emerald-300 flex items-center gap-2"
                  >
                    <span>{s.name}</span>
                    <span className="px-1.5 py-0.2 rounded-md bg-emerald-200/70 dark:bg-emerald-900 text-[10px] font-bold">
                      {s.demand_percentage}%
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Actionable Recommendations */}
            <div className="bg-blue-50 dark:bg-blue-950/30 rounded-2xl border border-blue-200 dark:border-blue-900/40 p-6">
              <h3 className="text-sm font-bold text-blue-950 dark:text-blue-200 mb-2">
                Tailored Learning Pathway
              </h3>
              <ul className="space-y-1.5 text-xs text-blue-900 dark:text-blue-300">
                {result.recommendations.map((rec, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="text-blue-500 font-bold">•</span>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
