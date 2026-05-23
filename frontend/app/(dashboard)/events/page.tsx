const events = [
  ["Acme Energy", "Infrastructure Expansion", "Growth +0.82", "0.89"],
  ["North Rail", "Transit Permit", "Investment +0.75", "0.84"],
  ["CloudOps", "Regional Hiring", "Economic +0.68", "0.79"],
];

export default function Page() {
  return <div className="space-y-5"><h1 className="text-3xl font-semibold">Event Intelligence</h1><div className="grid md:grid-cols-3 gap-4">{["Entities", "Event Types", "Confidence Avg"].map((x,i)=><div key={x} className="rounded-xl border p-4 bg-white dark:bg-slate-900"><p className="text-sm text-slate-500">{x}</p><p className="text-2xl font-bold">{[212,17,'0.83'][i]}</p></div>)}</div><div className="rounded-xl border p-4 bg-white dark:bg-slate-900"><div className="space-y-3">{events.map((r)=><div key={r[0]} className="rounded-lg border p-3"><p className="font-medium">{r[0]} · {r[1]}</p><p className="text-sm text-slate-500">{r[2]} · Confidence {r[3]}</p></div>)}</div></div></div>;
}
