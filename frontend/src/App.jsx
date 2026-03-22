import { useEffect, useState } from "react"

// App is the root component — the first thing that renders when someone opens Recall.
function App() {
  // useState creates a variable 'status' that React watches.
  // When status changes, React automatically re-renders the component.
  // We start it as null meaning "we haven't fetched anything yet"
  const [status, setStatus] = useState(null)

  // useEffect runs code AFTER the component first appears on screen.
  // The empty [] at the end means "only run this once on first load"
  useEffect(() => {
    // Call our FastAPI backend's health check endpoint
    // Because of the proxy in vite.config.js, /api/health
    // automatically gets forwarded to http://localhost:8000/health
    fetch("/api/health")
      .then(res => res.json())
      .then(data => setStatus(data.status))
      .catch(() => setStatus("error"))
  }, [])

  return (
    <div style={{ 
      display: "flex", 
      flexDirection: "column",
      alignItems: "center", 
      justifyContent: "center", 
      height: "100vh",
      gap: "16px"
    }}>
      <h1 style={{ color: "#00d4e8", fontSize: "48px", fontWeight: "700" }}>
        Recall.
      </h1>
      <p style={{ color: "#ffffff" }}>
        Backend status: {" "}
        <span style={{ color: status === "healthy" ? "#00d4e8" : "#ff4444" }}>
          {status === null ? "checking..." : status}
        </span>
      </p>
    </div>
  )
}

export default App
