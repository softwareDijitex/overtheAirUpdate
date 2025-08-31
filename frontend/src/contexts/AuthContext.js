
// import React, { createContext, useContext, useState, useEffect } from "react";
// import axios from "axios";
// import { API_BASE_URL } from "../config";

// const AuthContext = createContext();

// export function useAuth() {
//   return useContext(AuthContext);
// }

// // Function to decode JWT token
// const decodeToken = (token) => {
//   try {
//     const base64Url = token.split(".")[1];
//     const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
//     const jsonPayload = decodeURIComponent(
//       atob(base64)
//         .split("")
//         .map(function (c) {
//           return "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2);
//         })
//         .join("")
//     );
//     return JSON.parse(jsonPayload);
//   } catch (error) {
//     console.error("Error decoding token:", error);
//     return null;
//   }
// };

// export function AuthProvider({ children }) {
//   // ✅ Load token from localStorage on startup
//   const [token, setToken] = useState(() => localStorage.getItem("token"));
//   const [user, setUser] = useState(null);

//   // ✅ Restore user info from token on app load/refresh
//   useEffect(() => {
//     if (token) {
//       const decodedToken = decodeToken(token);
//       if (decodedToken) {
//         setUser({
//           customer_id: decodedToken.customer_id,
//           email: decodedToken.email,
//           is_admin: decodedToken.is_admin,
//         });
//       }
//     }
//   }, [token]);

//   // Set up axios interceptor to include token in all requests
//   useEffect(() => {
//     const interceptor = axios.interceptors.request.use(
//       (config) => {
//         if (token) {
//           config.headers.Authorization = `Bearer ${token}`;
//         }
//         return config;
//       },
//       (error) => Promise.reject(error)
//     );
//     return () => {
//       axios.interceptors.request.eject(interceptor);
//     };
//   }, [token]);

//   const login = async (email, password) => {
//     try {
//       const response = await axios.post(`${API_BASE_URL}/api/customers/login`, {
//         email,
//         password,
//       });

//       if (response.data.token) {
//         setToken(response.data.token);
//         localStorage.setItem("token", response.data.token); // ✅ persist token

//         const decodedToken = decodeToken(response.data.token);
//         if (decodedToken) {
//           setUser({
//             // ...response.data,
//             customer_id: decodedToken.customer_id,
//             email: decodedToken.email,
//             is_admin: decodedToken.is_admin,
//           });
//         } else {
//           setUser(response.data);
//         }
//         return { success: true };
//       } else {
//         return { success: false, error: "Login failed" };
//       }
//     } catch (error) {
//       console.error("Login error:", error);
//       return {
//         success: false,
//         error:
//           error.response?.data?.detail ||
//           error.response?.data?.message ||
//           "Login failed",
//       };
//     }
//   };

//   const adminLogin = async (email, password) => {
//     try {
//       const response = await axios.post(
//         `${API_BASE_URL}/api/customers/admin/login`,
//         {
//           email,
//           password,
//         }
//       );

//       if (response.data.token) {
//         setToken(response.data.token);
//         localStorage.setItem("token", response.data.token); // ✅ persist token

//         const decodedToken = decodeToken(response.data.token);
//         if (decodedToken) {
//           setUser({
//             // ...response.data,
//             customer_id: decodedToken.customer_id,
//             email: decodedToken.email,
//             is_admin: decodedToken.is_admin,
//           });
//         } else {
//           setUser(response.data);
//         }
//         return { success: true };
//       } else {
//         return { success: false, error: "Admin login failed" };
//       }
//     } catch (error) {
//       console.error("Admin login error:", error);
//       return {
//         success: false,
//         error:
//           error.response?.data?.detail ||
//           error.response?.data?.message ||
//           "Admin login failed",
//       };
//     }
//   };

//   const register = async (userData) => {
//     try {
//       const response = await axios.post(
//         `${API_BASE_URL}/api/customers/register`,
//         userData
//       );

//       if (response.data.token) {
//         setToken(response.data.token);
//         localStorage.setItem("token", response.data.token); // ✅ persist token

//         const decodedToken = decodeToken(response.data.token);
//         if (decodedToken) {
//           setUser({
//             ...response.data,
//             customer_id: decodedToken.customer_id,
//             email: decodedToken.email,
//             is_admin: decodedToken.is_admin,
//           });
//         } else {
//           setUser(response.data);
//         }
//         return { success: true };
//       } else {
//         return { success: false, error: "Registration failed" };
//       }
//     } catch (error) {
//       console.error("Registration error:", error);
//       return {
//         success: false,
//         error:
//           error.response?.data?.detail ||
//           error.response?.data?.message ||
//           "Registration failed",
//       };
//     }
//   };

//   const logout = () => {
//     setToken(null);
//     setUser(null);
//     localStorage.removeItem("token"); // ✅ clear storage
//   };

//   const value = {
//     token,
//     user,
//     login,
//     adminLogin,
//     register,
//     logout,
//   };

//   return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
// }


import React, { createContext, useContext, useEffect, useMemo, useState } from "react"; // CHANGED
import axios from "axios";
import { API_BASE_URL } from "../config";

const AuthContext = createContext();

export function useAuth() {
  return useContext(AuthContext);
}

// Function to decode JWT token (unchanged)
const decodeToken = (token) => {
  try {
    const base64Url = token.split(".")[1];
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split("")
        .map(function (c) {
          return "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2);
        })
        .join("")
    );
    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error("Error decoding token:", error);
    return null;
  }
};

export function AuthProvider({ children }) {
  // ✅ Start empty and restore from localStorage once on mount
  const [token, setToken] = useState(null); // CHANGED (was: useState(() => localStorage.getItem("token")))
  const [user, setUser] = useState(null);
  const [isRestoring, setIsRestoring] = useState(true); // NEW

  // NEW: single place to persist and hydrate session from a JWT
  const saveSession = (jwt) => {
    setToken(jwt);
    localStorage.setItem("token", jwt);
    const decoded = decodeToken(jwt);
    if (decoded) {
      setUser({
        customer_id: decoded.customer_id,
        email: decoded.email,
        is_admin: !!decoded.is_admin,
      });
    } else {
      setUser(null);
    }
  };

  // ✅ Restore user info from token on first mount
  useEffect(() => {
    const stored = localStorage.getItem("token"); // CHANGED (moved into this effect)
    if (stored) {
      saveSession(stored); // NEW
    }
    setIsRestoring(false); // NEW
  }, []);

  // Set up axios interceptor to include token in all requests (unchanged behavior)
  useEffect(() => {
    const interceptor = axios.interceptors.request.use(
      (config) => {
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );
    return () => {
      axios.interceptors.request.eject(interceptor);
    };
  }, [token]);

  // NEW (optional but handy): auto-logout on 401 responses
  useEffect(() => {
    const respInterceptor = axios.interceptors.response.use(
      (r) => r,
      (error) => {
        if (error?.response?.status === 401) {
          logout();
        }
        return Promise.reject(error);
      }
    );
    return () => axios.interceptors.response.eject(respInterceptor);
  }, []);

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/customers/login`, {
        email,
        password,
      });

      if (response.data.token) {
        saveSession(response.data.token); // CHANGED
        return { success: true };
      } else {
        return { success: false, error: "Login failed" };
      }
    } catch (error) {
      console.error("Login error:", error);
      return {
        success: false,
        error:
          error.response?.data?.detail ||
          error.response?.data?.message ||
          "Login failed",
      };
    }
  };

  const adminLogin = async (email, password) => {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/customers/admin/login`,
        { email, password }
      );

      if (response.data.token) {
        saveSession(response.data.token); // CHANGED
        return { success: true };
      } else {
        return { success: false, error: "Admin login failed" };
      }
    } catch (error) {
      console.error("Admin login error:", error);
      return {
        success: false,
        error:
          error.response?.data?.detail ||
          error.response?.data?.message ||
          "Admin login failed",
      };
    }
  };

  const register = async (userData) => {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/customers/register`,
        userData
      );

      if (response.data.token) {
        saveSession(response.data.token); // CHANGED
        return { success: true };
      } else {
        return { success: false, error: "Registration failed" };
      }
    } catch (error) {
      console.error("Registration error:", error);
      return {
        success: false,
        error:
          error.response?.data?.detail ||
          error.response?.data?.message ||
          "Registration failed",
      };
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem("token"); // ✅ clear storage (unchanged)
  };

  const value = useMemo( // NEW: memoize context for stability
    () => ({
      token,
      user,
      isRestoring,       // NEW
      isAdmin: !!user?.is_admin, // NEW (convenience)
      login,
      adminLogin,
      register,
      logout,
    }),
    [token, user, isRestoring]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
