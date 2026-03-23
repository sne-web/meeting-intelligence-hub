import Navbar from "../components/Navbar"

function Dashboard() {
  const workspace = localStorage.getItem("recall_workspace") || "Workspace"

  return (
    <div className="min-h-screen">
      <Navbar />
      <div className="max-w-7xl mx-auto px-6 py-12">
        <h1 className="text-3xl font-bold text-white mb-2">
          Good to see you, {workspace} 👋
        </h1>
        <p className="text-gray-400">
          Upload your first meeting transcript to get started.
        </p>
      </div>
    </div>
  )
}

export default Dashboard