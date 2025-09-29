        export default function MessageBubble({ role, content }: any){
  return <div className={'message '+(role==='user'?'user':'assistant')}>{content}</div>
}
