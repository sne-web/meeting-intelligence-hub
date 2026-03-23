import { useNavigate, useLocation } from "react-router-dom"

function Navbar() {
  const navigate = useNavigate()
  const location = useLocation()
  const workspace = localStorage.getItem("recall_workspace") || "Workspace"

  function isActive(path) {
    return location.pathname === path
  }

  return (
    <nav className="w-full bg-[#161b22] border-b border-[#21262d] px-6 py-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between">

        <button
          onClick={() => navigate("/dashboard")}
          className="text-2xl font-bold text-white hover:opacity-80 transition-opacity"
        >
          Recall<span className="text-[#00d4e8]">.</span>
        </button>

        <div className="flex items-center gap-6">
          <button
            onClick={() => navigate("/dashboard")}
            className={`text-sm transition-colors ${
              isActive("/dashboard") ? "text-[#00d4e8] font-medium" : "text-gray-400 hover:text-white"
            }`}
          >
            Dashboard
          </button>
          <button
            onClick={() => navigate("/upload")}
            className={`text-sm transition-colors ${
              isActive("/upload") ? "text-[#00d4e8] font-medium" : "text-gray-400 hover:text-white"
            }`}
          >
            Upload
          </button>
        </div>

        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-[#00d4e8]"></div>
          <span className="text-gray-400 text-sm">{workspace}</span>
        </div>

      </div>
    </nav>
  )
}

export default Navbar