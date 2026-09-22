import React from 'react';
import { FlaskConical, Building2 } from 'lucide-react';

interface Props {
  labs: string[];
}

export default function LabGuidance({ labs }: Props) {
  if (!labs || labs.length === 0) {
    return null;
  }

  return (
    <div className="bg-slate-800/80 backdrop-blur border border-slate-700 rounded-2xl p-6 shadow-xl">
      <div className="flex items-center gap-2 mb-4">
        <FlaskConical className="w-5 h-5 text-emerald-400" />
        <h3 className="text-md font-bold text-white">Testing & Laboratory Guidance</h3>
      </div>

      <div className="space-y-2.5">
        {labs.map((lab, index) => (
          <div
            key={index}
            className="bg-slate-900/60 p-3.5 rounded-xl border border-slate-700/60 flex items-start gap-3"
          >
            <Building2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
            <div className="text-xs text-slate-300 leading-relaxed font-sans">
              {lab}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
