// src/Guards.js
import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "./contexts/AuthContext";

const centeredSpinner = (
  <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh" }}>
    <div className="spinner-border text-primary" role="status">
      <span className="visually-hidden">Loading...</span>
    </div>
  </div>
);

export function PrivateRoute({ children }) {
  const { user, isRestoring } = useAuth();
  if (isRestoring) return centeredSpinner;
  return user ? children : <Navigate to="/login" replace />;
}

export function AdminRoute({ children }) {
  const { user, isRestoring } = useAuth();
  if (isRestoring) return centeredSpinner;
  if (!user) return <Navigate to="/admin/login" replace />;
  if (!user.is_admin) return <Navigate to="/unauthorized" replace />;
  return children;
}
