import { useState, useEffect } from "react"
import { useNavigate, useLocation } from "react-router-dom"

function Navbar() {
  const navigate = useNavigate()
  const location = useLocation()
  const [profileName, setProfileName] = useState("Profile")
  const [profileEmail, setProfileEmail] = useState("")
  const [showDropdown, setShowDropdown] = useState(false)

  useEffect(() => {
    fetch("/api/auth/me", {
      headers: { "Authorization": `Bearer ${localStorage.getItem("token")}` }
    })
    .then(r => r.json())
    .then(data => { 
        if (data.full_name) setProfileName(data.full_name)
        else setProfileName("Configure Profile")
        if (data.email) setProfileEmail(data.email)
    })
    .catch(() => {})
  }, [])

  function handleLogout() {
    localStorage.removeItem("token")
    navigate("/login")
  }

  async function handleDeleteAccount() {
    if (!confirm("Are you incredibly sure you want to permanently wipe all of your data? This action cannot be undone.")) return;
    try {
      const res = await fetch("/api/auth/me", {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${localStorage.getItem("token")}` }
      })
      
      if (!res.ok) {
        const errorData = await res.json()
        alert(`Deletion failed: ${errorData.detail}`)
        return
      }
      
      localStorage.removeItem("token")
      navigate("/login")
    } catch (e) {
      alert("Failed to wipe data")
    }
  }

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

        <div className="relative">
          <button 
            onClick={() => setShowDropdown(!showDropdown)}
            className="flex items-center gap-2 hover:bg-[#21262d] px-3 py-2 rounded-xl transition-colors"
          >
            <div className="w-2 h-2 rounded-full bg-[#00d4e8]"></div>
            <span className="text-gray-400 text-sm whitespace-nowrap">{profileName.substring(0, 15)}{profileName.length > 15 && "..."}</span>
          </button>
          
          {showDropdown && (
            <div className="absolute right-0 mt-2 w-56 bg-[#161b22] border border-[#21262d] rounded-xl shadow-2xl py-1 z-50">
                {profileEmail && (
                  <div className="px-4 py-3 text-xs text-gray-400 truncate border-b border-[#21262d] mb-1 bg-[#0d1117]/50 rounded-t-xl font-medium">
                    {profileEmail}
                  </div>
                )}
                <button 
                  onClick={handleLogout}
                  className="w-full text-left px-4 py-2 text-sm text-gray-300 hover:text-white hover:bg-[#21262d] transition-colors"
                >
                  Log out
                </button>
                <div className="border-t border-[#21262d] my-1"></div>
                <button 
                  onClick={handleDeleteAccount}
                  className="w-full text-left px-4 py-2 text-sm text-red-500 hover:bg-red-500/10 transition-colors"
                >
                  Delete account
                </button>
            </div>
          )}
        </div>

      </div>
    </nav>
  )
}

export default Navbar