// src/Guards.js
import { Navigate } from "react-router-dom";
// ⬇⬇⬇ Make sure this path matches your actual folder name and file
import { useAuth } from "./contexts/AuthContext";

export function PrivateRoute({ children }) {
  const { user, isRestoring } = useAuth();
  if (isRestoring) return null; // or a loader component
  return user ? children : <Navigate to="/login" replace />;
}

export function AdminRoute({ children }) {
  const { user, isRestoring } = useAuth();
  if (isRestoring) return null; // or a loader component
  if (!user) return <Navigate to="/admin/login" replace />;
  if (!user.is_admin) return <Navigate to="/unauthorized" replace />;
  return children;
}
