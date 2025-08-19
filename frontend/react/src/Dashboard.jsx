import { useEffect, useState } from 'react'

export default function Dashboard(){
  const [signals, setSignals] = useState([])
  useEffect(()=>{
    fetch('http://localhost:8000/signals').then(r=>r.json()).then(setSignals)
    const es = new EventSource('http://localhost:8000/stream/signals')
    es.onmessage = () => fetch('http://localhost:8000/signals').then(r=>r.json()).then(setSignals)
    return ()=> es.close()
  },[])
  return (
    <div style={{fontFamily:'system-ui,-apple-system,Segoe UI,Roboto,Ubuntu'}}>
      <header style={{position:'sticky',top:0,background:'#000',color:'#fff',padding:'12px 16px'}}>
        <div style={{fontWeight:600,fontSize:18}}>MarketAI – Realtime</div>
        <div style={{opacity:.8,fontSize:12}}>Experimentální nástroj, nikoli investiční poradenství.</div>
      </header>
      <main style={{padding:16, maxWidth:1080, margin:'0 auto'}}>
        <div style={{background:'#fff',borderRadius:16,boxShadow:'0 6px 20px rgba(0,0,0,.06)',padding:16}}>
          <h2 style={{marginTop:0}}>Živé signály</h2>
          <div style={{overflowX:'auto'}}>
            <table style={{width:'100%',borderCollapse:'collapse'}}>
              <thead>
                <tr style={{textAlign:'left',color:'#666',fontSize:14}}>
                  <th style={{padding:'8px 4px'}}>Čas (UTC)</th>
                  <th>Ticker</th>
                  <th>Směr</th>
                  <th>Pravděp.</th>
                  <th>Důvody</th>
                </tr>
              </thead>
              <tbody>
                {signals.map(s => (
                  <tr key={s.id} style={{borderTop:'1px solid #eee'}}>
                    <td style={{padding:'8px 4px'}}>{new Date(s.ts).toLocaleString()}</td>
                    <td><strong>{s.symbol}</strong></td>
                    <td>{s.direction}</td>
                    <td>{(s.prob*100).toFixed(1)}%</td>
                    <td style={{color:'#444'}}>{s.reasons}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  )
}
