const opportunities = [
  ["Austin Utility Corridor", "Acme Power", "High", "0.91", "Immediate outreach"],
  ["Bay Area Industrial Lease", "CloudOps", "Medium", "0.78", "Schedule discovery call"],
];

export default function Page() {
  return <div className="space-y-5"><h1 className="text-3xl font-semibold">Lead Opportunity Scoring</h1><div className="grid gap-3">{opportunities.map((o)=><div key={o[0]} className="rounded-xl border p-4 bg-white dark:bg-slate-900"><p className="font-medium">{o[0]}</p><p className="text-sm text-slate-500">Entity: {o[1]} · Impact: {o[2]} · Confidence: {o[3]}</p><p className="text-sm mt-2">Action: {o[4]}</p></div>)}</div></div>;
}
