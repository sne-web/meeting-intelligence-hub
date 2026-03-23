import { useState, useEffect } from "react"
import Navbar from "../components/Navbar"
import { useNavigate } from "react-router-dom"

function Dashboard() {
  const workspace = localStorage.getItem("recall_workspace") || "Workspace"
  const navigate = useNavigate()

  // meetings — list of all uploaded meetings fetched from the backend
  const [meetings, setMeetings] = useState([])
  // loading — true while we're fetching from the backend
  const [loading, setLoading] = useState(true)
  // error — any error message to show
  const [error, setError] = useState("")

  // Fetch meetings when the Dashboard first loads
  useEffect(() => {
    fetchMeetings()
  }, [])

  async function fetchMeetings() {
    try {
      const response = await fetch("/api/transcripts/")
      if (!response.ok) throw new Error("Failed to fetch meetings")
      const data = await response.json()
      setMeetings(data.meetings)
    } catch (err) {
      setError("Could not load meetings. Is the backend running?")
    } finally {
      setLoading(false)
    }
  }

  // Format the date nicely e.g. "March 23, 2026"
  function formatDate(isoString) {
    return new Date(isoString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric"
    })
  }

  // Calculate total action items across all meetings
  const totalActionItems = meetings.reduce(
    (sum, m) => sum + (m.action_items_count || 0), 0
  )

  return (
    <div className="min-h-screen">
      <Navbar />

      <div className="max-w-7xl mx-auto px-6 py-12">

        {/* Header */}
        <div className="flex items-center justify-between mb-10">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">
              Good to see you, {workspace} 👋
            </h1>
            <p className="text-gray-400">
              {meetings.length === 0
                ? "Upload your first meeting transcript to get started."
                : `You have ${meetings.length} meeting${meetings.length > 1 ? "s" : ""} in your workspace.`}
            </p>
          </div>
          <button
            onClick={() => navigate("/upload")}
            className="bg-[#00d4e8] hover:bg-[#00b8cc] text-[#0d1117] 
                       font-semibold px-6 py-3 rounded-xl transition-colors text-sm"
          >
            + Upload Transcript
          </button>
        </div>

        {/* Stats row — only show if there are meetings */}
        {meetings.length > 0 && (
          <div className="grid grid-cols-3 gap-4 mb-10">
            <div className="bg-[#161b22] border border-[#21262d] rounded-2xl p-6">
              <p className="text-gray-400 text-sm mb-1">Total Meetings</p>
              <p className="text-3xl font-bold text-white">{meetings.length}</p>
            </div>
            <div className="bg-[#161b22] border border-[#21262d] rounded-2xl p-6">
              <p className="text-gray-400 text-sm mb-1">Action Items</p>
              <p className="text-3xl font-bold text-[#00d4e8]">{totalActionItems}</p>
            </div>
            <div className="bg-[#161b22] border border-[#21262d] rounded-2xl p-6">
              <p className="text-gray-400 text-sm mb-1">Processed</p>
              <p className="text-3xl font-bold text-white">
                {meetings.filter(m => m.status === "processed").length}
                <span className="text-gray-500 text-lg font-normal">
                  /{meetings.length}
                </span>
              </p>
            </div>
          </div>
        )}

        {/* Loading state */}
        {loading && (
          <div className="text-center py-20">
            <p className="text-gray-400">Loading meetings...</p>
          </div>
        )}

        {/* Error state */}
        {error && (
          <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-xl">
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        )}

        {/* Empty state — no meetings yet */}
        {!loading && !error && meetings.length === 0 && (
          <div className="text-center py-20 border-2 border-dashed 
                          border-[#21262d] rounded-2xl">
            <div className="text-5xl mb-4">🎙️</div>
            <h2 className="text-white font-semibold text-lg mb-2">
              No meetings yet
            </h2>
            <p className="text-gray-400 text-sm mb-6">
              Upload a transcript to start extracting insights
            </p>
            <button
              onClick={() => navigate("/upload")}
              className="bg-[#00d4e8] hover:bg-[#00b8cc] text-[#0d1117] 
                         font-semibold px-6 py-3 rounded-xl transition-colors text-sm"
            >
              Upload your first transcript
            </button>
          </div>
        )}

        {/* Meetings grid */}
        {!loading && meetings.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {meetings.map((meeting) => (
              <div
                key={meeting.id}
                onClick={() => navigate(`/meeting/${meeting.id}`)}
                className="bg-[#161b22] border border-[#21262d] hover:border-[#00d4e8]/50 
                           rounded-2xl p-6 cursor-pointer transition-colors group"
              >
                {/* Meeting filename */}
                <div className="flex items-start justify-between mb-4">
                  <h3 className="text-white font-medium text-sm leading-tight 
                                 group-hover:text-[#00d4e8] transition-colors">
                    {meeting.filename}
                  </h3>
                  {/* Status badge */}
                  <span className={`text-xs px-2 py-1 rounded-full ml-2 flex-shrink-0 ${
                    meeting.status === "processed"
                      ? "bg-green-500/10 text-green-400 border border-green-500/20"
                      : "bg-yellow-500/10 text-yellow-400 border border-yellow-500/20"
                  }`}>
                    {meeting.status === "processed" ? "✓ Processed" : "⏳ Uploaded"}
                  </span>
                </div>

                {/* Stats */}
                <div className="space-y-2 text-xs text-gray-500">
                  <div className="flex items-center justify-between">
                    <span>📅 {formatDate(meeting.upload_date)}</span>
                    <span>{meeting.word_count?.toLocaleString()} words</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>
                      🎤 {meeting.speakers?.length > 0
                        ? `${meeting.speakers.length} speaker${meeting.speakers.length > 1 ? "s" : ""}`
                        : "No speakers detected"}
                    </span>
                    <span>
                      {meeting.action_items_count > 0
                        ? `${meeting.action_items_count} action items`
                        : "Not analysed yet"}
                    </span>
                  </div>
                </div>

                {/* Hover arrow */}
                <div className="mt-4 text-[#00d4e8] text-xs opacity-0 
                                group-hover:opacity-100 transition-opacity">
                  View details →
                </div>
              </div>
            ))}
          </div>
        )}

      </div>
    </div>
  )
}

export default Dashboard