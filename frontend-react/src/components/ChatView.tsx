        import { useEffect, useState } from 'react'
import MessageBubble from './MessageBubble'
export default function ChatView({ chat, token }: any){
  const [messages, setMessages] = useState<any[]>([])
  const [input, setInput] = useState('')
  const API = import.meta.env.VITE_API_URL || 'http://0.0.0.0:8000'
  useEffect(()=>{ if(chat) fetchMessages() }, [chat])
  async function fetchMessages(){ const r = await fetch(`${API}/chats/${chat.id}/messages`, { headers:{ Authorization: 'Bearer '+token } }); const j = await r.json(); setMessages(j) }
  async function send(){ if(!input) return; await fetch(`${API}/chats/${chat.id}/messages`, { method:'POST', headers:{'Content-Type':'application/json', Authorization:'Bearer '+token}, body: JSON.stringify({ role:'user', content: input }) }); setInput(''); fetchMessages() }
  return (<div className='chatview'><h2>{chat.title}</h2><div className='messages'>{messages.map((m:any,i:number)=>(<MessageBubble key={i} role={m.role} content={m.content}/>))}</div><div className='composer'><input value={input} onChange={e=>setInput(e.target.value)} placeholder='Ask something...' /><button onClick={send}>Send</button></div></div>)
}
