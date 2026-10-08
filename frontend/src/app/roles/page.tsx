"use client";

import { useEffect, useState } from "react";

interface RoleSkill {
  name: string;
  count: number;
  percentage: number;
}

interface RoleComparisonItem {
  role: string;
  job_count: number;
  skills: RoleSkill[];
}

export default function RolesPage() {
  const [data, setData] = useState<RoleComparisonItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchComparison() {
      setLoading(true);
      try {
        const res = await fetch("/api/analytics/role-comparison");
        if (res.ok) {
          const list = await res.json();
          setData(list || []);
        }
      } catch (e) {
        console.error("Error fetching role comparison:", e);
      } finally {
        setLoading(false);
      }
    }
    fetchComparison();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-gray-200/60 dark:border-gray-800/80">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-400 bg-clip-text text-transparent">
            Job Role Skill Comparison
          </h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Compare skill profiles and expectations across major engineering disciplines
          </p>
        </div>
        <div className="text-xs font-semibold px-3 py-1.5 rounded-xl bg-blue-50 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300 self-start sm:self-center">
          {data.length} Roles Profiled
        </div>
      </div>

      {loading ? (
        <div className="py-20 text-center text-sm text-gray-500 animate-pulse">
          Analyzing role competencies...
        </div>
      ) : data.length === 0 ? (
        <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 p-12 text-center text-xs text-gray-500">
          No role data available. Load sample jobs or run collection first.
        </div>
      ) : (
        <div className="space-y-8">
          {/* Role Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {data.map((item) => (
              <div
                key={item.role}
                className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200/80 dark:border-gray-800 p-6 shadow-sm flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-base font-extrabold text-gray-900 dark:text-white">
                      {item.role}
                    </h2>
                    <span className="text-xs font-bold text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/60 px-2.5 py-1 rounded-lg">
                      {item.job_count} listings
                    </span>
                  </div>

                  <div className="space-y-3">
                    {item.skills.map((s, idx) => (
                      <div key={s.name}>
                        <div className="flex items-center justify-between text-xs font-medium mb-1">
                          <span className="text-gray-700 dark:text-gray-300 font-semibold">
                            {idx + 1}. {s.name}
                          </span>
                          <span className="font-bold text-gray-900 dark:text-white">
                            {s.percentage}%
                          </span>
                        </div>
                        <div className="w-full h-1.5 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-blue-600 rounded-full"
                            style={{ width: `${Math.min(s.percentage, 100)}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="mt-6 pt-4 border-t border-gray-100 dark:border-gray-800/80 text-[11px] text-gray-400 flex items-center justify-between">
                  <span>Top requisite:</span>
                  <span className="font-bold text-gray-700 dark:text-gray-300">
                    {item.skills[0]?.name || "N/A"}
                  </span>
                </div>
              </div>
            ))}
          </div>

          {/* Overlap & Distinction Analysis Card */}
          <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200/80 dark:border-gray-800 p-6 shadow-sm space-y-4">
            <h3 className="text-base font-bold text-gray-900 dark:text-white">
              Core Tech Stack Foundations
            </h3>
            <p className="text-xs text-gray-500 leading-relaxed">
              Regardless of specialization, tech jobs consistently require universal foundational competencies: 
              <strong className="text-gray-800 dark:text-gray-200"> Git, Docker, REST APIs, and System Design</strong>.
              Specialization happens on top of this foundation with role-specific frameworks (e.g., React & Next.js for Frontend, FastAPI & Kafka for Backend, Kubernetes & Terraform for DevOps).
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
