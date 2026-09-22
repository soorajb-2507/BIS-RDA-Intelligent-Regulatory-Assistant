import React from 'react';
import { Award, GitBranch } from 'lucide-react';

interface Props {
  standards: string[];
  paths: string[];
}

export default function StandardsPath({ standards, paths }: Props) {
  if ((!standards || standards.length === 0) && (!paths || paths.length === 0)) {
    return null;
  }

  return (
    <div className="bg-slate-800/80 backdrop-blur border border-slate-700 rounded-2xl p-6 shadow-xl">
      <div className="flex items-center gap-2 mb-4">
        <Award className="w-5 h-5 text-amber-400" />
        <h3 className="text-md font-bold text-white">Applicable Standards & Certification Path</h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Standards List */}
        <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-700/60">
          <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
            Identified BIS Standards
          </h4>
          <div className="flex flex-wrap gap-2">
            {standards.map((std, i) => (
              <span
                key={i}
                className="px-3 py-1.5 rounded-lg bg-blue-500/15 border border-blue-500/30 text-blue-300 font-mono text-xs font-bold"
              >
                {std}
              </span>
            ))}
          </div>
        </div>

        {/* Certification Route */}
        <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-700/60">
          <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
            <GitBranch className="w-3.5 h-3.5 text-indigo-400" />
            <span>Certification Route</span>
          </h4>
          {paths && paths.length > 0 ? (
            <ul className="space-y-2 text-xs text-slate-300">
              {paths.map((p, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 mt-1.5 shrink-0" />
                  <span>{p}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-xs text-slate-500 italic">No specific certification route required or cited.</p>
          )}
        </div>
      </div>
    </div>
  );
}
