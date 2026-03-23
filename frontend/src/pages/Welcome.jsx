import { useState } from "react"
import { useNavigate } from "react-router-dom"

function Welcome() {
  const [name, setName] = useState("")
  const [error, setError] = useState("")
  const navigate = useNavigate()

  function handleStart() {
    if (!name.trim()) {
      setError("Please enter a workspace name to continue")
      return
    }
    localStorage.setItem("recall_workspace", name.trim())
    navigate("/dashboard")
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4">
      <h1 className="text-6xl font-bold text-white mb-2">
  Recall<span className="text-[#00d4e8]">.</span>
</h1>
      <p className="text-gray-400 mb-12 text-lg">Never lose what was said again.</p>

      <div className="w-full max-w-md bg-[#161b22] border border-[#21262d] rounded-2xl p-8">
        <h2 className="text-white text-xl font-semibold mb-2">Welcome — let's get started</h2>
        <p className="text-gray-400 text-sm mb-6">Enter a workspace name to begin.</p>

        <input
          type="text"
          placeholder="e.g. Acme Corp, My Team, Personal..."
          value={name}
          onChange={(e) => { setName(e.target.value); setError("") }}
          onKeyDown={(e) => e.key === "Enter" && handleStart()}
          className="w-full bg-[#0d1117] border border-[#21262d] text-white
                     placeholder-gray-600 rounded-xl px-4 py-3 text-sm
                     focus:outline-none focus:border-[#00d4e8] transition-colors"
        />

        {error && <p className="text-red-400 text-xs mt-2">{error}</p>}

        <button
          onClick={handleStart}
          className="w-full mt-4 bg-[#00d4e8] hover:bg-[#00b8cc] text-[#0d1117]
                     font-semibold py-3 rounded-xl transition-colors text-sm"
        >
          Enter Workspace →
        </button>
      </div>

      <p className="text-gray-600 text-xs mt-8">
        Powered by Claude AI · Built for Cymonic Technologies Hackathon
      </p>
    </div>
  )
}

export default Welcome