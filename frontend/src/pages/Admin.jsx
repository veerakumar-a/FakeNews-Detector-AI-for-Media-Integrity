import React, { useEffect, useState } from 'react'
import axios from 'axios'

export default function Admin() {
  const [votes, setVotes] = useState({})
  const [subs, setSubs] = useState([])
  const [loading, setLoading] = useState(false)

  async function load() {
    setLoading(true)
    try {
      const [v, s] = await Promise.all([
        axios.get('http://127.0.0.1:8000/admin/votes'),
        axios.get('http://127.0.0.1:8000/admin/subscriptions'),
      ])
      setVotes(v.data.votes || {})
      setSubs(s.data.subscriptions || [])
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  return (
    <div className="pt-20 p-6 max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">Admin — Demo</h1>
      <div className="mb-4">
        <button onClick={load} className="button-glow">Refresh</button>
      </div>

      <section className="glassmorphism p-4 mb-6">
        <h2 className="text-xl font-semibold">Votes</h2>
        {loading ? <div>Loading...</div> : (
          <ul className="mt-2">
            {Object.keys(votes).length === 0 && <li className="text-sm text-gray-400">No votes yet</li>}
            {Object.entries(votes).map(([id, score]) => (
              <li key={id} className="py-1">{id}: <strong>{score}</strong></li>
            ))}
          </ul>
        )}
      </section>

      <section className="glassmorphism p-4">
        <h2 className="text-xl font-semibold">Subscriptions</h2>
        {loading ? <div>Loading...</div> : (
          <div>
            <div className="text-sm text-gray-400">Total: {subs.length}</div>
            <ul className="mt-2">
              {subs.map((s) => (
                <li key={s.id} className="py-1">{s.channel} — {s.address} <span className="text-xs text-gray-500">{s.created_at}</span></li>
              ))}
            </ul>
          </div>
        )}
      </section>
    </div>
  )
}
