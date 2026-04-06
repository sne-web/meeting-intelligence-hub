import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import Welcome from "./pages/Welcome"
import Dashboard from "./pages/Dashboard"
import Upload from "./pages/Upload"
import MeetingDetail from "./pages/MeetingDetail"
import Login from "./pages/Login"
import Register from "./pages/Register"

function PrivateRoute({ children }) {
  const token = localStorage.getItem("token")
  return token ? children : <Navigate to="/login" />
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Welcome />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dashboard" element={
          <PrivateRoute><Dashboard /></PrivateRoute>
        } />
        <Route path="/upload" element={
          <PrivateRoute><Upload /></PrivateRoute>
        } />
        <Route path="/meeting/:id" element={
          <PrivateRoute><MeetingDetail /></PrivateRoute>
        } />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App