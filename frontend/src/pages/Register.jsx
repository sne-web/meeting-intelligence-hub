import { useState } from "react"
import { useNavigate, Link } from "react-router-dom"

function Register() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  async function handleRegister(e) {
    if (e) e.preventDefault()
    if (!email || !password) {
      setError("Please fill in all fields")
      return
    }
    if (password.length < 6) {
      setError("Password must be at least 6 characters")
      return
    }
    
    setLoading(true)
    setError("")
    
    try {
      const response = await fetch("http://localhost:8000/api/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ email, password })
      })
      
      const data = await response.json()
      
      if (!response.ok) {
        throw new Error(data.detail || "Registration failed")
      }
      
      localStorage.setItem("token", data.access_token)
      navigate("/dashboard")
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#0d1117] flex flex-col items-center justify-center px-4 relative">
      <div className="absolute top-6 left-6">
        <Link to="/" className="text-2xl font-bold text-white hover:opacity-80 transition-opacity">
          Recall<span className="text-[#00d4e8]">.</span>
        </Link>
      </div>
      
      <div className="w-full max-w-md bg-[#161b22] border border-[#21262d] rounded-2xl p-8 shadow-2xl relative z-10">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Create an account</h1>
          <p className="text-gray-400">Sign up to get started</p>
        </div>

        <form onSubmit={handleRegister} className="space-y-5">
          <div>
            <label className="block text-gray-400 text-sm mb-2">Email Address</label>
            <input
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-[#0d1117] border border-[#21262d] text-white
                         placeholder-gray-600 rounded-xl px-4 py-3 text-sm
                         focus:outline-none focus:border-[#00d4e8] transition-colors"
            />
          </div>
          
          <div>
            <label className="block text-gray-400 text-sm mb-2">Password</label>
            <input
              type="password"
              placeholder="Create a password (min 6 chars)"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-[#0d1117] border border-[#21262d] text-white
                         placeholder-gray-600 rounded-xl px-4 py-3 text-sm
                         focus:outline-none focus:border-[#00d4e8] transition-colors"
            />
          </div>

          {error && <p className="text-red-400 text-xs text-center bg-red-400/10 py-2 rounded-lg">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-2 bg-[#00d4e8] hover:bg-[#00b8cc] text-[#0d1117]
                       font-semibold py-3 rounded-xl transition-colors text-sm disabled:opacity-50"
          >
            {loading ? "Creating account..." : "Sign Up"}
          </button>
        </form>

        <p className="text-gray-400 text-sm text-center mt-6">
          Already have an account? <Link to="/login" className="text-[#00d4e8] hover:underline">Log in</Link>
        </p>
      </div>
    </div>
  )
}

export default Register
