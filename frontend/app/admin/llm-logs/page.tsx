'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api-client';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface Interaction {
  timestamp: string;
  stage: string;
  provider: string;
  model: string;
  prompt: string;
  system_prompt?: string;
  response?: string;
  error?: string;
}

export default function LLMLogsPage() {
  const [items, setItems] = useState<Interaction[]>([]);
  const [loading, setLoading] = useState(false);
  const [stage, setStage] = useState('');
  const [provider, setProvider] = useState('');
  const [model, setModel] = useState('');

  const load = async () => {
    setLoading(true);
    try {
      const data = await apiClient.listLLMInteractions({ stage: stage || undefined, provider: provider || undefined, model: model || undefined, limit: 200 });
      setItems(data.data || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">LLM Interactions</h1>
      <div className="flex gap-2 mb-4">
        <Input placeholder="Stage (e.g., requirements, architecture)" value={stage} onChange={(e) => setStage(e.target.value)} />
        <Input placeholder="Provider (openai, anthropic, deepseek)" value={provider} onChange={(e) => setProvider(e.target.value)} />
        <Input placeholder="Model" value={model} onChange={(e) => setModel(e.target.value)} />
        <Button onClick={load} disabled={loading}>{loading ? 'Loading...' : 'Refresh'}</Button>
      </div>
      <div className="space-y-4">
        {items.map((it, idx) => (
          <Card key={idx}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Badge variant="outline">{new Date(it.timestamp).toLocaleString()}</Badge>
                <Badge variant="secondary">{it.stage}</Badge>
                <Badge>{it.provider}</Badge>
                <Badge variant="outline">{it.model}</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-slate-500 mb-1">System Prompt</div>
                  <pre className="bg-slate-50 p-3 rounded text-xs overflow-x-auto whitespace-pre-wrap">{it.system_prompt || '-'}</pre>
                  <div className="text-sm text-slate-500 mt-3 mb-1">User Prompt</div>
                  <pre className="bg-slate-50 p-3 rounded text-xs overflow-x-auto whitespace-pre-wrap">{it.prompt}</pre>
                </div>
                <div>
                  <div className="text-sm text-slate-500 mb-1">Response</div>
                  {it.error ? (
                    <pre className="bg-red-50 p-3 rounded text-xs overflow-x-auto whitespace-pre-wrap text-red-700">{it.error}</pre>
                  ) : (
                    <pre className="bg-slate-50 p-3 rounded text-xs overflow-x-auto whitespace-pre-wrap">{it.response}</pre>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
        {!items.length && <div className="text-slate-500">No interactions found.</div>}
      </div>
    </div>
  );
}


