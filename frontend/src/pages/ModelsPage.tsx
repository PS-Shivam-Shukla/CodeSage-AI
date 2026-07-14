interface ModelInfo {
  name: string;
  type: 'LLM' | 'Embedding';
  provider: string;
  status: 'active' | 'available';
}

const MODELS: ModelInfo[] = [
  { name: 'Meta Llama 3.1 70B',  type: 'LLM',       provider: 'Meta / Together AI', status: 'active'    },
  { name: 'Meta Llama 3.1 8B',   type: 'LLM',       provider: 'Meta / Together AI', status: 'available' },
  { name: 'BAAI/bge-m3',         type: 'Embedding', provider: 'BAAI',               status: 'active'    },
  { name: 'BAAI/bge-large-en-v1.5', type: 'Embedding', provider: 'BAAI',            status: 'available' },
];

export function ModelsPage() {
  return (
    <div className="flex flex-col gap-stack-md">
      <div className="mb-stack-lg">
        <h2 className="text-display text-on-surface mb-2">Models</h2>
        <p className="text-body-lg text-on-surface-variant">
          Manage and switch LLM and embedding models.
        </p>
      </div>

      <div className="glass-card rounded-xl shadow-sm overflow-hidden">
        <div className="p-6 border-b border-outline-variant/20 flex items-center gap-3">
          <div className="w-9 h-9 bg-primary/10 text-primary rounded-lg flex items-center justify-center">
            <span className="material-symbols-outlined">psychology</span>
          </div>
          <h3 className="text-headline-md">Available Models</h3>
        </div>

        <div className="divide-y divide-outline-variant/10">
          {MODELS.map((m) => (
            <div key={m.name} className="flex items-center justify-between px-6 py-4 hover:bg-surface-container/40 transition-colors">
              <div className="flex items-center gap-4">
                <div className={`px-2 py-0.5 rounded-full text-label-caps font-label-caps uppercase text-xs ${
                  m.type === 'LLM'
                    ? 'bg-tertiary-fixed text-on-tertiary-fixed'
                    : 'bg-secondary-container text-on-secondary-container'
                }`}>
                  {m.type}
                </div>
                <div>
                  <p className="text-body-md font-semibold text-on-surface font-code-snippet">{m.name}</p>
                  <p className="text-body-sm text-on-surface-variant">{m.provider}</p>
                </div>
              </div>
              <span className={`flex items-center gap-1.5 text-body-sm font-semibold ${
                m.status === 'active' ? 'text-secondary' : 'text-outline'
              }`}>
                <span className={`w-2 h-2 rounded-full ${m.status === 'active' ? 'bg-secondary' : 'bg-outline'}`} />
                {m.status === 'active' ? 'Active' : 'Available'}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
