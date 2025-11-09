// src/components/ResultView.jsx
import React, { useState } from 'react'
import { CircularProgressbar } from 'react-circular-progressbar'
import 'react-circular-progressbar/dist/styles.css'
import axios from 'axios'

export default function ResultView({ result }){
  const score = Math.round(result.confidence * 100)
  const [summary, setSummary] = useState(null)
  const [factChecks, setFactChecks] = useState([])
  const [bias, setBias] = useState(null)
  const [voteScore, setVoteScore] = useState(0)

  async function loadSummary(){
    try{
      const r = await axios.post('http://127.0.0.1:8000/summarize', { text: result.raw_text || result.highlighted })
      setSummary(r.data.summary)
    }catch(e){
      console.error(e)
    }
  }

  async function loadFactChecks(){
    try{
      const r = await axios.post('http://127.0.0.1:8000/fact-check', { text: result.raw_text || result.highlighted })
      setFactChecks(r.data.results || [])
    }catch(e){
      console.error(e)
    }
  }

  async function loadBias(){
    try{
      const r = await axios.post('http://127.0.0.1:8000/bias', { text: result.raw_text || result.highlighted })
      setBias(r.data)
    }catch(e){
      console.error(e)
    }
  }

  async function vote(delta){
    try{
      const r = await axios.post('http://127.0.0.1:8000/community/vote', { item_id: result.id || 'item-1', vote: delta })
      setVoteScore(r.data.score)
    }catch(e){
      console.error(e)
    }
  }

  return (
    <div style={{marginTop:20, width:'80%', background:'#071022', padding:18, borderRadius:10, border:'1px solid #21303f'}}>
      <div style={{display:'flex', gap:18, alignItems:'center'}}>
        <div style={{width:80,height:80}}>
          <CircularProgressbar value={score} text={`${score}%`} />
        </div>
        <div>
          <h2 style={{margin:0, fontSize:20}}>Verdict: {result.label}</h2>
          <div style={{color:'#9fb0c8'}}>Sentiment: {result.sentiment?.tone} (polarity: {result.sentiment?.polarity})</div>
          {result.source && <div style={{color:'#9fb0c8'}}>Source: {result.source.domain} ({result.source.status})</div>}
        </div>
      </div>
      <div style={{marginTop:12, color:'#dbeafe'}} dangerouslySetInnerHTML={{__html: result.highlighted}} />
      <div style={{marginTop:12, color:'#9fb0c8'}}>Keywords: {result.keywords?.slice(0,12).join(', ')}</div>

      <div style={{marginTop:14, display:'flex', gap:8}}>
        <button className="button-glow" onClick={loadSummary}>Generate Summary</button>
        <button className="button-glow" onClick={loadFactChecks}>Find Fact-Checks</button>
        <button className="button-glow" onClick={loadBias}>Analyze Bias</button>
      </div>

      {summary && (
        <div style={{marginTop:12, padding:12, background:'#07182a', borderRadius:8}}>
          <h3 style={{margin:0}}>Summary</h3>
          <p style={{marginTop:8, color:'#dbeafe'}}>{summary}</p>
        </div>
      )}

      {factChecks.length > 0 && (
        <div style={{marginTop:12}}>
          <h3 style={{margin:0}}>Fact-Checked Alternatives</h3>
          <ul style={{marginTop:8}}>
            {factChecks.map((f, i) => (
              <li key={i} style={{marginBottom:8}}>
                <a href={f.url} target="_blank" rel="noreferrer" style={{color:'#7ee3d3'}}>{f.title}</a>
                <div style={{color:'#9fb0c8'}}>{f.source} — {f.summary}</div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {bias && (
        <div style={{marginTop:12, padding:12, background:'#07182a', borderRadius:8}}>
          <h3 style={{margin:0}}>Bias Detection</h3>
          <div style={{marginTop:8, color:'#dbeafe'}}>{bias.label} — score: {bias.score}</div>
        </div>
      )}

      <div style={{marginTop:12, display:'flex', gap:8, alignItems:'center'}}>
        <button onClick={() => vote(+1)} className="p-2 rounded bg-dark-800/40">Upvote</button>
        <button onClick={() => vote(-1)} className="p-2 rounded bg-dark-800/40">Downvote</button>
        <div style={{color:'#9fb0c8'}}>Community score: {voteScore}</div>
      </div>
    </div>
  )
}
