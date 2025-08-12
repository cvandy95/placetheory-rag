import type { NextApiRequest, NextApiResponse } from 'next'

const RAG_API_URL = process.env.RAG_API_URL || 'http://localhost:8000'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' })
  try {
    const { question, top_k = 6, where } = req.body || {}
    const response = await fetch(`${RAG_API_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, top_k, where }),
    })
    const data = await response.json()
    res.status(200).json(data)
  } catch (e: any) {
    res.status(500).json({ error: e.message })
  }
}
