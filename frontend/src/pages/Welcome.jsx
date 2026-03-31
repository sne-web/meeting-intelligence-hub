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
    <div className="min-h-screen bg-[#0d1117] flex flex-col items-center justify-center px-4 relative overflow-hidden">
      
      {/* Header */}
      <div className="absolute top-0 w-full p-6 flex justify-between items-center max-w-7xl mx-auto z-10">
        <h1 className="text-2xl font-bold text-white">
          Recall<span className="text-[#00d4e8]">.</span>
        </h1>
      </div>

      {/* Hero Content */}
      <div className="text-center w-full max-w-4xl mt-24 z-10 relative flex flex-col items-center">
        <div className="absolute -top-32 left-1/2 -translate-x-1/2 w-96 h-96 bg-[#00d4e8] rounded-full mix-blend-screen filter blur-[128px] opacity-20"></div>
        <h2 className="text-5xl md:text-7xl font-extrabold text-white mb-6 leading-tight">
          Never lose what was <span className="text-[#00d4e8]">said again.</span>
        </h2>
        <p className="text-gray-400 text-lg md:text-xl mb-12 max-w-2xl mx-auto leading-relaxed">
          The ultimate meeting intelligence platform. Automatically transcribe, analyze, and extract insights from your conversations with unparalleled accuracy.
        </p>
        
        {/* Workspace Login Card */}
        <div className="w-full max-w-md bg-[#161b22]/90 backdrop-blur-md border border-[#21262d] rounded-2xl p-8 shadow-2xl relative text-left">
          <h2 className="text-white text-2xl font-semibold mb-2">Get Started</h2>
          <p className="text-gray-400 text-sm mb-6">Enter a workspace name to begin.</p>

          <input
            type="text"
            placeholder="e.g. Acme Corp, My Team, Personal..."
            value={name}
            onChange={(e) => { 
                setName(e.target.value); 
                setError(""); 
            }}
            onKeyDown={(e) => e.key === "Enter" && handleStart()}
            className="w-full bg-[#0d1117] border border-[#21262d] text-white
                       placeholder-gray-600 rounded-xl px-4 py-3 text-sm
                       focus:outline-none focus:border-[#00d4e8] transition-colors"
          />

          {error && <p className="text-red-400 text-xs mt-2">{error}</p>}

          <button
            onClick={handleStart}
            className="w-full mt-6 bg-[#00d4e8] hover:bg-[#00b8cc] text-[#0d1117]
                       font-semibold py-3 rounded-xl transition-all shadow-[0_0_15px_rgba(0,212,232,0.2)] hover:shadow-[0_0_25px_rgba(0,212,232,0.4)] text-sm"
          >
            Enter Workspace →
          </button>
        </div>
      </div>

      {/* Feature Grid */}
      <div className="mt-24 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl w-full z-10 relative pb-12">
        <div className="bg-[#161b22]/80 backdrop-blur-sm border border-[#21262d] p-8 rounded-2xl hover:border-[#00d4e8]/50 transition-colors group">
          <div className="h-12 w-12 bg-[#00d4e8]/10 rounded-xl flex items-center justify-center mb-6 group-hover:bg-[#00d4e8]/20 transition-colors">
            <svg className="w-6 h-6 text-[#00d4e8]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" /></svg>
          </div>
          <h3 className="text-white text-xl font-semibold mb-3">Flawless Transcription</h3>
          <p className="text-gray-400">Capture every word accurately with state-of-the-art speech recognition technology.</p>
        </div>
        <div className="bg-[#161b22]/80 backdrop-blur-sm border border-[#21262d] p-8 rounded-2xl hover:border-[#00d4e8]/50 transition-colors group">
          <div className="h-12 w-12 bg-[#00d4e8]/10 rounded-xl flex items-center justify-center mb-6 group-hover:bg-[#00d4e8]/20 transition-colors">
            <svg className="w-6 h-6 text-[#00d4e8]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
          </div>
          <h3 className="text-white text-xl font-semibold mb-3">Instant Insights</h3>
          <p className="text-gray-400">Automatically generate summaries, action items, and key takeaways immediately after the call.</p>
        </div>
        <div className="bg-[#161b22]/80 backdrop-blur-sm border border-[#21262d] p-8 rounded-2xl hover:border-[#00d4e8]/50 transition-colors group">
          <div className="h-12 w-12 bg-[#00d4e8]/10 rounded-xl flex items-center justify-center mb-6 group-hover:bg-[#00d4e8]/20 transition-colors">
            <svg className="w-6 h-6 text-[#00d4e8]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
          </div>
          <h3 className="text-white text-xl font-semibold mb-3">Intelligent Search</h3>
          <p className="text-gray-400">Find exactly what was discussed months ago with powerful semantic search capabilities.</p>
        </div>
      </div>
    </div>
  )
}

export default Welcome