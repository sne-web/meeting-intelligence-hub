import { useState, useEffect } from "react"
import { useParams, useNavigate } from "react-router-dom"
import Navbar from "../components/Navbar"

function MeetingDetail() {
  // useParams reads the meeting ID from the URL e.g. /meeting/abc-123
  const { id } = useParams()
  const navigate = useNavigate()

  const [meeting, setMeeting] = useState(null)
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(true)
  const [analysing, setAnalysing] = useState(false)
  const [activeTab, setActiveTab] = useState("decisions")
  const [error, setError] = useState("")

  useEffect(() => {
    fetchMeeting()
  }, [id])

  async function fetchMeeting() {
    try {
      // Fetch meeting metadata
      const res = await fetch(`/api/transcripts/${id}`)
      if (!res.ok) throw new Error("Meeting not found")
      const data = await res.json()
      setMeeting(data)

      // If already processed, fetch the analysis too
      if (data.status === "processed") {
        const analysisRes = await fetch(`/api/analysis/${id}`)
        if (analysisRes.ok) {
          const analysisData = await analysisRes.json()
          setAnalysis(analysisData)
        }
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleAnalyse() {
    setAnalysing(true)
    setError("")
    try {
      // This calls Claude to analyse the transcript
      // It may take 10-20 seconds depending on transcript length
      const res = await fetch(`/api/analysis/analyse/${id}`, {
        method: "POST"
      })
      if (!res.ok) throw new Error("Analysis failed")
      const data = await res.json()
      setAnalysis(data)
      setMeeting(prev => ({ ...prev, status: "processed" }))
    } catch (err) {
      setError("Analysis failed. Please check your API key and try again.")
    } finally {
      setAnalysing(false)
    }
  }

  function getSentimentColor(sentiment) {
    const colors = {
      positive: "text-green-400",
      negative: "text-red-400",
      neutral: "text-gray-400",
      mixed: "text-yellow-400",
      conflict: "text-red-400",
      agreement: "text-green-400"
    }
    return colors[sentiment] || "text-gray-400"
  }

  function getSentimentBg(sentiment) {
    const colors = {
      positive: "bg-green-500/10 border-green-500/20",
      negative: "bg-red-500/10 border-red-500/20",
      neutral: "bg-gray-500/10 border-gray-500/20",
      mixed: "bg-yellow-500/10 border-yellow-500/20"
    }
    return colors[sentiment] || "bg-gray-500/10 border-gray-500/20"
  }

  function getPriorityColor(priority) {
    const colors = {
      high: "text-red-400 bg-red-500/10 border-red-500/20",
      medium: "text-yellow-400 bg-yellow-500/10 border-yellow-500/20",
      low: "text-green-400 bg-green-500/10 border-green-500/20"
    }
    return colors[priority?.toLowerCase()] || "text-gray-400 bg-gray-500/10 border-gray-500/20"
  }

  if (loading) {
    return (
      <div className="min-h-screen">
        <Navbar />
        <div className="flex items-center justify-center py-20">
          <p className="text-gray-400">Loading meeting...</p>
        </div>
      </div>
    )
  }

  if (error && !meeting) {
    return (
      <div className="min-h-screen">
        <Navbar />
        <div className="max-w-7xl mx-auto px-6 py-12">
          <p className="text-red-400">{error}</p>
          <button
            onClick={() => navigate("/dashboard")}
            className="mt-4 text-[#00d4e8] text-sm"
          >
            ← Back to Dashboard
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen">
      <Navbar />

      <div className="max-w-7xl mx-auto px-6 py-8">

        {/* Header */}
        <div className="flex items-start justify-between mb-8">
          <div>
            <button
              onClick={() => navigate("/dashboard")}
              className="text-gray-500 hover:text-white text-sm mb-3 
                         transition-colors flex items-center gap-1"
            >
              ← Back to Dashboard
            </button>
            <h1 className="text-2xl font-bold text-white">{meeting?.filename}</h1>
            <div className="flex items-center gap-4 mt-2 text-sm text-gray-400">
              <span>📅 {new Date(meeting?.upload_date).toLocaleDateString()}</span>
              <span>📝 {meeting?.word_count?.toLocaleString()} words</span>
              <span>🎤 {meeting?.speakers?.join(", ") || "No speakers detected"}</span>
            </div>
          </div>

          {/* Analyse button — only shows if not yet processed */}
          {meeting?.status !== "processed" && (
            <button
              onClick={handleAnalyse}
              disabled={analysing}
              className="bg-[#00d4e8] hover:bg-[#00b8cc] disabled:opacity-50
                         disabled:cursor-not-allowed text-[#0d1117] font-semibold 
                         px-6 py-3 rounded-xl transition-colors text-sm"
            >
              {analysing ? "Analysing with Claude..." : "✨ Analyse with AI"}
            </button>
          )}
        </div>

        {/* Error message */}
        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl">
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        )}

        {/* Analysing loading state */}
        {analysing && (
          <div className="mb-6 p-6 bg-[#161b22] border border-[#21262d] rounded-xl">
            <div className="flex items-center gap-3">
              <div className="w-2 h-2 rounded-full bg-[#00d4e8] animate-pulse"></div>
              <p className="text-white text-sm">
                Claude is reading your transcript and extracting insights...
              </p>
            </div>
            <p className="text-gray-500 text-xs mt-2 ml-5">
              This usually takes 15-30 seconds depending on transcript length.
            </p>
          </div>
        )}

        {/* Not yet analysed state */}
        {meeting?.status !== "processed" && !analysing && (
          <div className="text-center py-16 border-2 border-dashed 
                          border-[#21262d] rounded-2xl">
            <div className="text-5xl mb-4">✨</div>
            <h2 className="text-white font-semibold text-lg mb-2">
              Ready to analyse
            </h2>
            <p className="text-gray-400 text-sm mb-6 max-w-md mx-auto">
              Click "Analyse with AI" above to extract decisions, action items, 
              and sentiment from this transcript using Claude.
            </p>
          </div>
        )}

        {/* Analysis results — only shows after processing */}
        {analysis && (
          <>
            {/* Sentiment overview banner */}
            {analysis.sentiment && (
              <div className={`p-4 rounded-xl border mb-6 ${getSentimentBg(analysis.sentiment.overall_sentiment)}`}>
                <div className="flex items-center justify-between">
                  <div>
                    <span className="text-white text-sm font-medium">Overall meeting tone: </span>
                    <span className={`text-sm font-semibold capitalize ${getSentimentColor(analysis.sentiment.overall_sentiment)}`}>
                      {analysis.sentiment.overall_sentiment}
                    </span>
                  </div>
                  <span className="text-gray-400 text-xs">
                    Score: {analysis.sentiment.overall_score?.toFixed(2)}
                  </span>
                </div>
                <p className="text-gray-400 text-xs mt-2">
                  {analysis.sentiment.summary}
                </p>
              </div>
            )}

            {/* Tabs */}
            <div className="flex gap-1 mb-6 bg-[#161b22] p-1 rounded-xl 
                            border border-[#21262d] w-fit">
              {["decisions", "action_items", "sentiment"].map(tab => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-4 py-2 rounded-lg text-sm transition-colors ${
                    activeTab === tab
                      ? "bg-[#00d4e8] text-[#0d1117] font-semibold"
                      : "text-gray-400 hover:text-white"
                  }`}
                >
                  {tab === "decisions" && `Decisions (${analysis.decisions?.length || 0})`}
                  {tab === "action_items" && `Action Items (${analysis.action_items?.length || 0})`}
                  {tab === "sentiment" && "Sentiment"}
                </button>
              ))}
            </div>

            {/* Decisions tab */}
            {activeTab === "decisions" && (
              <div className="space-y-3">
                {analysis.decisions?.length === 0 && (
                  <p className="text-gray-400 text-sm">No decisions found in this transcript.</p>
                )}
                {analysis.decisions?.map((decision, i) => (
                  <div key={i} className="bg-[#161b22] border border-[#21262d] 
                                          rounded-xl p-5">
                    <div className="flex items-start gap-3">
                      <span className="text-[#00d4e8] text-sm font-mono mt-0.5">
                        {String(i + 1).padStart(2, "0")}
                      </span>
                      <div>
                        <p className="text-white text-sm font-medium">
                          {decision.description}
                        </p>
                        {decision.context && (
                          <p className="text-gray-500 text-xs mt-1">
                            {decision.context}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Action Items tab */}
            {activeTab === "action_items" && (
              <div>
                {analysis.action_items?.length === 0 && (
                  <p className="text-gray-400 text-sm">No action items found.</p>
                )}
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-[#21262d]">
                        <th className="text-left text-gray-500 text-xs font-medium pb-3 pr-4">WHO</th>
                        <th className="text-left text-gray-500 text-xs font-medium pb-3 pr-4">WHAT</th>
                        <th className="text-left text-gray-500 text-xs font-medium pb-3 pr-4">BY WHEN</th>
                        <th className="text-left text-gray-500 text-xs font-medium pb-3">PRIORITY</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#21262d]">
                      {analysis.action_items?.map((item, i) => (
                        <tr key={i}>
                          <td className="py-4 pr-4">
                            <span className="text-[#00d4e8] text-sm font-medium">
                              {item.who}
                            </span>
                          </td>
                          <td className="py-4 pr-4">
                            <span className="text-white text-sm">{item.what}</span>
                          </td>
                          <td className="py-4 pr-4">
                            <span className="text-gray-400 text-sm">{item.by_when}</span>
                          </td>
                          <td className="py-4">
                            <span className={`text-xs px-2 py-1 rounded-full border ${getPriorityColor(item.priority)}`}>
                              {item.priority}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Sentiment tab */}
            {activeTab === "sentiment" && analysis.sentiment && (
              <div className="space-y-6">

                {/* Flags */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {[
                    { key: "has_conflict", label: "Conflict detected", icon: "⚡" },
                    { key: "has_strong_agreement", label: "Strong agreement", icon: "🤝" },
                    { key: "has_frustration", label: "Frustration present", icon: "😤" },
                    { key: "has_enthusiasm", label: "Enthusiasm present", icon: "🚀" }
                  ].map(flag => (
                    <div
                      key={flag.key}
                      className={`p-4 rounded-xl border text-center ${
                        analysis.sentiment.flags?.[flag.key]
                          ? "bg-[#00d4e8]/10 border-[#00d4e8]/30"
                          : "bg-[#161b22] border-[#21262d] opacity-40"
                      }`}
                    >
                      <div className="text-2xl mb-1">{flag.icon}</div>
                      <p className="text-white text-xs">{flag.label}</p>
                    </div>
                  ))}
                </div>

                {/* Per speaker sentiment */}
                <div>
                  <h3 className="text-white font-medium mb-3 text-sm">
                    Per-speaker breakdown
                  </h3>
                  <div className="space-y-3">
                    {analysis.sentiment.speaker_sentiments?.map((s, i) => (
                      <div key={i} className="bg-[#161b22] border border-[#21262d] 
                                              rounded-xl p-4">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-white text-sm font-medium">
                            {s.speaker}
                          </span>
                          <span className={`text-xs font-medium capitalize 
                                           ${getSentimentColor(s.sentiment)}`}>
                            {s.sentiment} ({s.score?.toFixed(2)})
                          </span>
                        </div>
                        <p className="text-gray-500 text-xs">{s.notes}</p>
                        {/* Score bar */}
                        <div className="mt-2 h-1.5 bg-[#21262d] rounded-full overflow-hidden">
                          <div
                            className="h-full bg-[#00d4e8] rounded-full"
                            style={{
                              width: `${((s.score + 1) / 2) * 100}%`
                            }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Segments */}
                <div>
                  <h3 className="text-white font-medium mb-3 text-sm">
                    Discussion segments
                  </h3>
                  <div className="space-y-2">
                    {analysis.sentiment.segments?.map((seg, i) => (
                      <div key={i} className="flex items-center justify-between 
                                              bg-[#161b22] border border-[#21262d] 
                                              rounded-xl px-4 py-3">
                        <span className="text-white text-sm">{seg.topic}</span>
                        <div className="flex items-center gap-2">
                          <span className={`text-xs capitalize 
                                           ${getSentimentColor(seg.sentiment)}`}>
                            {seg.sentiment}
                          </span>
                          <span className="text-gray-600 text-xs">·</span>
                          <span className="text-gray-500 text-xs">{seg.intensity}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default MeetingDetail