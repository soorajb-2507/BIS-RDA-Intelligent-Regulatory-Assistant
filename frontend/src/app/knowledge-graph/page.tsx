'use client';

import React from 'react';
import Navbar from '@/components/Navbar';
import { Share2, ArrowRight, ShieldCheck, Award, FlaskConical, Building2, Layers } from 'lucide-react';

const GRAPH_NODES = [
  { step: '1', title: 'BIS Standard', desc: 'e.g. IS 10500:2012 / IS 14543:2018', icon: ShieldCheck, color: 'text-blue-400', border: 'border-blue-500/40', bg: 'bg-blue-950/20' },
  { step: '2', title: 'Product Definition', desc: 'Potable Drinking Water / Helmets', icon: Layers, color: 'text-indigo-400', border: 'border-indigo-500/40', bg: 'bg-indigo-950/20' },
  { step: '3', title: 'Raw Material', desc: 'Source water, Clinker, Polycarbonate', icon: Layers, color: 'text-cyan-400', border: 'border-cyan-500/40', bg: 'bg-cyan-950/20' },
  { step: '4', title: 'Industry Sector', desc: 'Food & Beverage / Automotive Safety', icon: Building2, color: 'text-purple-400', border: 'border-purple-500/40', bg: 'bg-purple-950/20' },
  { step: '5', title: 'Certification Scheme', desc: 'Scheme-I (Mandatory ISI Mark) / CRS', icon: Award, color: 'text-amber-400', border: 'border-amber-500/40', bg: 'bg-amber-950/20' },
  { step: '6', title: 'Testing Requirement', desc: 'Chemical, Microbiological, Impact', icon: FlaskConical, color: 'text-emerald-400', border: 'border-emerald-500/40', bg: 'bg-emerald-950/20' },
  { step: '7', title: 'Accredited Lab', desc: 'BIS Central Lab / NABL / ARAI', icon: Building2, color: 'text-teal-400', border: 'border-teal-500/40', bg: 'bg-teal-950/20' },
  { step: '8', title: 'Applicable Order/Rule', desc: 'BIS Act 2016 / Quality Control Order', icon: ShieldCheck, color: 'text-rose-400', border: 'border-rose-500/40', bg: 'bg-rose-950/20' },
];

export default function KnowledgeGraphPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-8">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Share2 className="w-6 h-6 text-amber-400" />
            <h1 className="text-2xl font-black text-white">Neo4j Regulatory Knowledge Graph</h1>
          </div>
          <p className="text-xs text-slate-400">
            Visualizing the 8-node regulatory relationship topology used by the RDA Engine for graph-based reasoning.
          </p>
        </div>

        {/* 8-Node Chain Visualization */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
          <h2 className="text-sm font-bold text-slate-300 uppercase tracking-wider">
            8-Stage Regulatory Chain Topology
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {GRAPH_NODES.map((node, i) => {
              const Icon = node.icon;
              return (
                <div
                  key={i}
                  className={`p-4 rounded-xl border ${node.border} ${node.bg} flex flex-col justify-between relative`}
                >
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 text-slate-400">
                        Node {node.step}
                      </span>
                      <Icon className={`w-4 h-4 ${node.color}`} />
                    </div>
                    <h3 className="text-sm font-bold text-white">{node.title}</h3>
                    <p className="text-xs text-slate-400 mt-1">{node.desc}</p>
                  </div>
                  {i < GRAPH_NODES.length - 1 && (
                    <div className="hidden lg:block absolute -right-3 top-1/2 -translate-y-1/2 z-10">
                      <ArrowRight className="w-4 h-4 text-slate-600" />
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Graph Query Capabilities */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl">
            <h3 className="text-sm font-bold text-white mb-2">Graph Relationship Traversal</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Neo4j enables the RDA Engine to discover multi-hop connections between product specifications and statutory compliance orders:
            </p>
            <pre className="mt-3 p-3 bg-slate-950 rounded-xl border border-slate-800 text-[11px] font-mono text-indigo-300 overflow-x-auto">
{`MATCH (s:Standard {number: "IS 10500:2012"})
-[:COVERS_PRODUCT]->(p:Product)
-[:USES_MATERIAL]->(m:Material)
-[:MANDATES_CERTIFICATION]->(c:Certification)
-[:REQUIRES_TESTING]->(t:Testing)
-[:PERFORMED_BY]->(l:Laboratory)
RETURN s, p, c, t, l;`}
            </pre>
          </div>

          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl">
            <h3 className="text-sm font-bold text-white mb-2">Continuous Regulatory Learning in Graph</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              When new amendments or testing rules are ingested, the Continuous Learning service updates the graph relationships dynamically without downtime:
            </p>
            <div className="mt-3 space-y-2 text-xs text-slate-300">
              <div className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800 flex items-center justify-between">
                <span>Total Registered Standards:</span>
                <span className="font-mono text-emerald-400 font-bold">3 Master Standards</span>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800 flex items-center justify-between">
                <span>Certification Schemes Linked:</span>
                <span className="font-mono text-blue-400 font-bold">Scheme-I (ISI Mark)</span>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800 flex items-center justify-between">
                <span>Testing Labs Network:</span>
                <span className="font-mono text-amber-400 font-bold">BIS Central & Recognized Labs</span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
