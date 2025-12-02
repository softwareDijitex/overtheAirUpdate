// import React from "react";
// import {
//   BrowserRouter as Router,
//   Route,
//   Routes,
//   Navigate,
// } from "react-router-dom";
// import { AuthProvider, useAuth } from "./contexts/AuthContext";
// import AdminDashboard from "./components/AdminDashboard";
// import AdminLogin from "./components/AdminLogin";
// import CustomerDashboard from "./components/CustomerDashboard";
// import CustomerLogin from "./components/Login"; // Import Login as CustomerLogin
// import Register from "./components/Register";

// function PrivateRoute({ children }) {
//   const { token } = useAuth();
//   return token ? children : <Navigate to="/login" />;
// }

// function AdminRoute({ children }) {
//   const { token, user } = useAuth();
//   return token && user?.is_admin ? children : <Navigate to="/admin/login" />;
// }

// function App() {
//   return (
//     <AuthProvider>
//       <Router>
//         <div className="App">
//           <Routes>
//             <Route path="/" element={<Navigate to="/login" />} />
//             <Route path="/login" element={<CustomerLogin />} />
//             <Route path="/register" element={<Register />} />
//             <Route path="/admin/login" element={<AdminLogin />} />
//             <Route
//               path="/dashboard"
//               element={
//                 <PrivateRoute>
//                   <CustomerDashboard />
//                 </PrivateRoute>
//               }
//             />
//             <Route
//               path="/admin/dashboard"
//               element={
//                 <AdminRoute>
//                   <AdminDashboard />
//                 </AdminRoute>
//               }
//             />
//           </Routes>
//         </div>
//       </Router>
//     </AuthProvider>
//   );
// }

// export default App;

// App.js
import React from "react";
import {
  BrowserRouter as Router,
  Route,
  Routes,
  Navigate,
} from "react-router-dom";
import { AuthProvider, useAuth } from "./contexts/AuthContext"; // CHANGED (no need to import useAuth here)
import AdminDashboard from "./components/AdminDashboard";
import AdminLogin from "./components/AdminLogin";
import CustomerDashboard from "./components/CustomerDashboard";
import CustomerLogin from "./components/Login";
import Register from "./components/Register";
import { PrivateRoute, AdminRoute } from "./Guards"; // NEW
import NewDashboard from "./components/NewDashboard";

// REMOVED: inline guards (we now use the shared ones in routes/Guards.jsx)
// function PrivateRoute({ children }) {
//   const { token } = useAuth();
//   return token ? children : <Navigate to="/login" />;
// }
// function AdminRoute({ children }) {
//   const { token, user } = useAuth();
//   return token && user?.is_admin ? children : <Navigate to="/admin/login" />;
// }

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            <Route path="/" element={<Navigate to="/login" replace />} /> {/* CHANGED: add replace */}
            <Route path="/login" element={<CustomerLogin />} />
            <Route path="/register" element={<Register />} />
            <Route path="/admin/login" element={<AdminLogin />} />

            <Route
              path="/dashboard"
              element={
                <PrivateRoute>
                  <CustomerDashboard />
                </PrivateRoute>
              }
            />

            <Route
              path="/admin/dashboard"
              element={
                <AdminRoute>
                  <AdminDashboard />
                </AdminRoute>
              }
            />

            <Route
              path="/newdashboard"
              element={
                <NewDashboard />
              }
            />

            {/* NEW: optional catch-all to keep routing tidy */}
            <Route path="*" element={<Navigate to="/login" replace />} /> {/* NEW */}
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
