import { useState } from 'react'
import './App.css'

const SERVER_URL = "http://localhost:8000"
const WS_URL = "ws://localhost:8000/ws"

function App() {
  const [url, setUrl] = useState<string>()
  const [fetched, setFetched] = useState<boolean>(false)
  const [message, setMessage] = useState<string>("")
  const [messageStore, setMessageStore] = useState<{role: string, content: string}[]>([])

  const scrapeHandler = () => {
    if (!url) {
      console.log("NO URL PROVIDED")
      return
    }
    scrape(url).then(d => {
      console.log(d)
      setFetched(true)
    })
  }
  const scrape = async (url: string) => {
    const res = await fetch(`${SERVER_URL}/ingest`, {
      method: "POST",
      body: JSON.stringify({ url: url })
    })
    return await res.json()
  }

  const ws = new WebSocket(WS_URL)
  ws.onopen = () => {
    console.log('we are in business')
  }

  ws.onmessage = (event) => {
    setMessageStore(messages => [...messages, {"role": "assistant", "content": event.data}])
  }

  const send = () => {
    messageStore.push({"role": "user", "content": message})
    setMessage("")
    ws.send(message)
  }
  
  return (
    <div>
      <div>What API documentation would you like to know more about?</div>

      <input onChange={e => setUrl(e.target.value)}/>
      <button onClick={scrapeHandler}>learn more</button>
      <div>
        {fetched && (
          <>
            <div>Let us start chatting!</div>
            
            {messageStore.map((msg, _) => {
              return (
                <div>
                  <strong>{msg.role}</strong>: {msg.content}
                </div>
              )
              
            })}
            <input value={message} onChange={(e) => setMessage(e.target.value)}/> <button onClick={send}>send</button>
          </>
        )}
      </div>
    </div>

  )
}

export default App
