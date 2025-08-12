import React, { useState } from 'react'

type Message = { role: 'user' | 'assistant', content: string, chunks?: any[] }

export default function RagChat({ dma, storeChain }: { dma?: string; storeChain?: string }) {
  const [loading, setLoading] = useState(false)
  const [messages, setMessages] = useState<Message[]>([])
  const [q, setQ] = useState('')

  const ask = async () => {
    if (!q.trim()) return
    const userMsg: Message = { role: 'user', content: q }
    setMessages(m => [...m, userMsg])
    setQ('')
    setLoading(true)
    try {
      const body = {
        question: q,
        top_k: 6,
        where: {
          ...(dma ? { dma } : {}),
          ...(storeChain ? { storeChain } : {}),
        },
      }
      const response = await fetch('/api/rag', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      const data = await response.json()
      const assistant: Message = { role: 'assistant', content: data.answer, chunks: data.chunks }
      setMessages(m => [...m, assistant])
    } catch (e: any) {
      setMessages(m => [...m, { role: 'assistant', content: `Error: ${e.message}` }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="border rounded-lg p-3 bg-white">
      <div className="text-sm font-medium mb-2">Ask AI (RAG)</div>
      <div className="space-y-2 max-h-64 overflow-auto text-sm">
        {messages.map((m, i) => (
          <div key={i} className={m.role === 'user' ? 'text-right' : ''}>
            <div className={`inline-block px-3 py-2 rounded ${m.role === 'user' ? 'bg-blue-50' : 'bg-gray-50'}`}>
              <div className="whitespace-pre-wrap">{m.content}</div>
              {m.role === 'assistant' && m.chunks?.length ? (
                <details className="mt-2">
                  <summary className="cursor-pointer">Sources</summary>
                  <ul className="list-disc pl-4">
                    {m.chunks.map((c: any, j: number) => (
                      <li key={j}>
                        <span className="font-mono text-xs">{c.metadata?.source || c.id}</span>
                      </li>
                    ))}
                  </ul>
                </details>
              ) : null}
            </div>
          </div>
        ))}
      </div>
      <div className="flex gap-2 mt-2">
        <input
          className="flex-1 border rounded px-3 py-2 text-sm"
          placeholder="Ask about the dashboard, metrics, methodology…"
          value={q}
          onChange={e => setQ(e.target.value)}
          onKeyDown={e => {
            if (e.key === 'Enter') ask()
          }}
        />
        <button
          onClick={ask}
          disabled={loading}
          className="border rounded px-3 py-2 text-sm"
        >
          {loading ? 'Thinking…' : 'Ask'}
        </button>
      </div>
    </div>
  )
}
