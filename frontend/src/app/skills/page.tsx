"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface Skill {
  id: number;
  name: string;
  canonical_name: string;
  category: string | null;
  description: string | null;
}

interface TopSkill {
  skill_id: number;
  skill_name: string;
  category: string | null;
  job_count: number;
  percentage: number;
}

const CATEGORIES = [
  "All",
  "Programming Languages",
  "Frontend",
  "Backend",
  "Cloud & DevOps",
  "Databases",
  "AI & Data",
  "Tools & Practices",
];

export default function SkillsPage() {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [demandMap, setDemandMap] = useState<Record<string, TopSkill>>({});
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      try {
        const [skillsRes, topRes] = await Promise.all([
          fetch("/api/skills"),
          fetch("/api/analytics/top-skills?limit=100"),
        ]);

        if (skillsRes.ok) {
          const list = await skillsRes.json();
          setSkills(list || []);
        }
        if (topRes.ok) {
          const topData = await topRes.json();
          const dMap: Record<string, TopSkill> = {};
          (topData.skills || []).forEach((item: TopSkill) => {
            dMap[item.skill_name.toLowerCase()] = item;
          });
          setDemandMap(dMap);
        }
      } catch (e) {
        console.error("Error fetching skills:", e);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const filteredSkills = skills.filter((s) => {
    const matchesCat =
      selectedCategory === "All" ||
      (s.category && s.category.toLowerCase() === selectedCategory.toLowerCase());
    const matchesSearch =
      search.trim() === "" ||
      s.name.toLowerCase().includes(search.toLowerCase()) ||
      s.canonical_name.toLowerCase().includes(search.toLowerCase());
    return matchesCat && matchesSearch;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-gray-200/60 dark:border-gray-800/80">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-400 bg-clip-text text-transparent">
            Canonical Skills Taxonomy
          </h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Standardized technical skills database mapped across industry job postings
          </p>
        </div>
        <div className="text-xs font-semibold px-3 py-1.5 rounded-xl bg-blue-50 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300 self-start sm:self-center">
          {skills.length} Standardized Skills
        </div>
      </div>

      {/* Search & Categories Bar */}
      <div className="space-y-3">
        <div className="relative max-w-md">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search skills by name..."
            className="w-full pl-9 pr-4 py-2 rounded-xl bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm"
          />
          <svg
            className="w-4 h-4 absolute left-3 top-3 text-gray-400"
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
        </div>

        {/* Category Pills */}
        <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-medium shrink-0 transition ${
                selectedCategory === cat
                  ? "bg-blue-600 text-white font-semibold shadow-sm"
                  : "bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Skills Grid */}
      {loading ? (
        <div className="py-20 text-center text-sm text-gray-500 animate-pulse">
          Loading taxonomy directory...
        </div>
      ) : filteredSkills.length === 0 ? (
        <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 p-12 text-center text-xs text-gray-500">
          No skills found matching &ldquo;{search}&rdquo;.
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {filteredSkills.map((s) => {
            const demand =
              demandMap[s.name.toLowerCase()] ||
              demandMap[s.canonical_name.toLowerCase()];
            return (
              <div
                key={s.id}
                className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200/80 dark:border-gray-800 p-5 shadow-sm hover:shadow-md transition flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start justify-between gap-2">
                    <h3 className="font-bold text-sm text-gray-900 dark:text-white">
                      {s.name}
                    </h3>
                    {demand && (
                      <span className="px-2 py-0.5 rounded-md text-[10px] font-bold bg-blue-50 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300">
                        {demand.percentage}%
                      </span>
                    )}
                  </div>

                  <p className="text-[11px] font-medium text-gray-500 dark:text-gray-400 mt-1">
                    {s.category || "General"}
                  </p>

                  {demand ? (
                    <div className="mt-3">
                      <div className="flex items-center justify-between text-[10px] text-gray-400 mb-1">
                        <span>Market Demand</span>
                        <span>{demand.job_count} listings</span>
                      </div>
                      <div className="w-full h-1.5 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-blue-600 rounded-full"
                          style={{ width: `${Math.min(demand.percentage, 100)}%` }}
                        />
                      </div>
                    </div>
                  ) : (
                    <div className="mt-3 text-[10px] text-gray-400">
                      Standard taxonomy skill
                    </div>
                  )}
                </div>

                <div className="mt-4 pt-3 border-t border-gray-100 dark:border-gray-800/80 flex items-center justify-between">
                  <span className="text-[10px] text-gray-400 font-mono">
                    ID #{s.id}
                  </span>
                  <Link
                    href={`/jobs?role=${encodeURIComponent(s.name)}`}
                    className="text-[11px] font-semibold text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1"
                  >
                    View Jobs
                    <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
                    </svg>
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
