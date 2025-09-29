        export default function ChatList({ chats, onSelect, activeChatId }: any){
  return (<div className='chat-list'>{chats.map((c:any)=>(<div key={c.id} className={'chat-item'+(activeChatId===c.id?' active':'' )} onClick={()=>onSelect(c)}>{c.title}</div>))}</div>)
}
