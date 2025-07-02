import { useEffect, useState } from 'react'
import './App.css'

const SERVER_URL = "http://localhost:8000"

function App() {
  const [data, setData] = useState(null)

  const fetchData = async () => {
    const res = await fetch(`${SERVER_URL}/test`, {
      method: 'GET'
    })
    const data = await res.json()
    return data
  }

  useEffect(() => {
    try {
      fetchData().then(d => setData(d.message))
    } catch (e) {
      console.log(e)
    }
  }, [])

  return (
    <div>{data}</div>
  )
}

export default App
