        import { useState, useEffect } from 'react'
import AuthForm from './components/AuthForm'
import ChatList from './components/ChatList'
import ChatView from './components/ChatView'

export default function App(){
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'))
  const [chats, setChats] = useState<any[]>([])
  const [selectedChat, setSelectedChat] = useState<any | null>(null)
  const API = import.meta.env.VITE_API_URL || 'http://0.0.0.0:8000'

  useEffect(()=>{ if(token) { localStorage.setItem('token', token); fetchChats() } }, [token])

  async function fetchChats(){
    const r = await fetch(API+'/chats', { headers: { Authorization: 'Bearer '+token } })
    setChats(await r.json())
  }

  if(!token) return <AuthForm onLoggedIn={(t:string)=>setToken(t)} />

  return (<div className='app'><aside className='sidebar'><h3>Chats</h3><button onClick={async ()=>{ await fetch(API+'/chats', { method:'POST', headers:{'Content-Type':'application/json', Authorization:'Bearer '+token}, body: JSON.stringify({title:'New Chat'}) }); fetchChats() }}>New Chat</button><ChatList chats={chats} activeChatId={selectedChat?.id||null} onSelect={setSelectedChat} /></aside><main className='main'>{selectedChat? <ChatView chat={selectedChat} token={token} /> : <div className='placeholder'>Select or create a chat</div>}</main></div>)
}
