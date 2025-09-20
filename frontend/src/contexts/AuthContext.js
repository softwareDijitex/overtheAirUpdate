
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


// import React, { createContext, useContext, useEffect, useMemo, useState } from "react"; // CHANGED
// import axios from "axios";
// import { API_BASE_URL } from "../config";

// const AuthContext = createContext();

// export function useAuth() {
//   return useContext(AuthContext);
// }

// // Function to decode JWT token (unchanged)
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
//   // ✅ Start empty and restore from localStorage once on mount
//   const [token, setToken] = useState(null); // CHANGED (was: useState(() => localStorage.getItem("token")))
//   const [user, setUser] = useState(null);
//   const [isRestoring, setIsRestoring] = useState(true); // NEW

//   // NEW: single place to persist and hydrate session from a JWT
//   const saveSession = (jwt) => {
//     setToken(jwt);
//     localStorage.setItem("token", jwt);
//     const decoded = decodeToken(jwt);
//     if (decoded) {
//       setUser({
//         customer_id: decoded.customer_id,
//         email: decoded.email,
//         is_admin: !!decoded.is_admin,
//       });
//     } else {
//       setUser(null);
//     }
//   };

//   // ✅ Restore user info from token on first mount
//   useEffect(() => {
//     const stored = localStorage.getItem("token"); // CHANGED (moved into this effect)
//     if (stored) {
//       saveSession(stored); // NEW
//     }
//     setIsRestoring(false); // NEW
//   }, []);

//   // Set up axios interceptor to include token in all requests (unchanged behavior)
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

//   // NEW (optional but handy): auto-logout on 401 responses
//   useEffect(() => {
//     const respInterceptor = axios.interceptors.response.use(
//       (r) => r,
//       (error) => {
//         if (error?.response?.status === 401) {
//           logout();
//         }
//         return Promise.reject(error);
//       }
//     );
//     return () => axios.interceptors.response.eject(respInterceptor);
//   }, []);

//   const login = async (email, password) => {
//     try {
//       const response = await axios.post(`${API_BASE_URL}/api/customers/login`, {
//         email,
//         password,
//       });

//       if (response.data.token) {
//         saveSession(response.data.token); // CHANGED
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
//         { email, password }
//       );

//       if (response.data.token) {
//         saveSession(response.data.token); // CHANGED
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
//         saveSession(response.data.token); // CHANGED
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
//     localStorage.removeItem("token"); // ✅ clear storage (unchanged)
//   };

//   const value = useMemo( // NEW: memoize context for stability
//     () => ({
//       token,
//       user,
//       isRestoring,       // NEW
//       isAdmin: !!user?.is_admin, // NEW (convenience)
//       login,
//       adminLogin,
//       register,
//       logout,
//     }),
//     [token, user, isRestoring]
//   );

//   return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
// }

import React, { createContext, useContext, useEffect, useMemo, useRef, useState } from "react";
import axios from "axios";
import { API_BASE_URL } from "../config";

const AuthContext = createContext();
export function useAuth() { return useContext(AuthContext); }

// ---- Keys
const TOKEN_KEY = "token";           // shared single token (whichever role is active)
const ROLE_KEY  = "activeRole";      // "admin" | "customer"

// ---- Helpers
const decodeToken = (token) => {
  try {
    const base64Url = token.split(".")[1];
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    const jsonPayload = decodeURIComponent(
      atob(base64).split("").map(c => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2)).join("")
    );
    return JSON.parse(jsonPayload);
  } catch (e) {
    console.error("Error decoding token:", e);
    return null;
  }
};

const roleOfToken = (jwt) => {
  const decoded = decodeToken(jwt);
  if (!decoded) return null;
  return decoded.is_admin ? "admin" : "customer";
};

export function AuthProvider({ children }) {
  const [token, setToken] = useState(null);       // in-memory token for THIS tab
  const [user, setUser] = useState(null);
  const [isRestoring, setIsRestoring] = useState(true);
  const [kickedByOtherRole, setKickedByOtherRole] = useState(false); // NEW

  // Optional: instant cross-tab messages (storage event is the fallback)
  const bcRef = useRef(typeof window !== "undefined" && "BroadcastChannel" in window ? new BroadcastChannel("auth") : null);

  // ---- Core session setters
  const saveSession = (jwt) => {
    const decoded = decodeToken(jwt);
    if (!decoded) {
      clearInMemory();
      return;
    }
    const role = decoded.is_admin ? "admin" : "customer";

    // Persist globally (affects ALL tabs)
    localStorage.setItem(TOKEN_KEY, jwt);
    localStorage.setItem(ROLE_KEY, role);

    // Set THIS tab's memory
    setToken(jwt);
    setUser({
      customer_id: decoded.customer_id,
      email: decoded.email,
      is_admin: !!decoded.is_admin,
    });

    setKickedByOtherRole(false); // reset any prior kick flag
    bcRef.current?.postMessage({ type: "LOGIN", role });
  };

  const clearInMemory = () => {
    setToken(null);
    setUser(null);
  };

  // Used when another tab with a DIFFERENT role took over
  const detachForRoleSwitch = () => {
    clearInMemory();              // don't touch localStorage; preserve the new role’s session
    setKickedByOtherRole(true);
  };

  const logout = () => {
    clearInMemory();
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(ROLE_KEY);
    setKickedByOtherRole(false);
    bcRef.current?.postMessage({ type: "LOGOUT" });
  };

  // ---- Initial restore (adopt whichever role/token is in localStorage)
  useEffect(() => {
    const stored = localStorage.getItem(TOKEN_KEY);
    if (stored) {
      // Adopt and hydrate; this tab will reflect the current global session
      saveSession(stored);
    }
    setIsRestoring(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ---- Axios interceptors
  useEffect(() => {
    const req = axios.interceptors.request.use(
      (config) => {
        if (token) config.headers.Authorization = `Bearer ${token}`;
        return config;
      },
      (error) => Promise.reject(error)
    );
    return () => axios.interceptors.request.eject(req);
  }, [token]);

  useEffect(() => {
    const resp = axios.interceptors.response.use(
      (r) => r,
      (error) => {
        if (error?.response?.status === 401) logout();
        return Promise.reject(error);
      }
    );
    return () => axios.interceptors.response.eject(resp);
  }, []);

  // ---- Cross-tab sync: BroadcastChannel (instant)
  useEffect(() => {
    const onMsg = (evt) => {
      const msg = evt?.data;
      if (!msg) return;

      const myRole = user ? (user.is_admin ? "admin" : "customer") : null;

      if (msg.type === "LOGIN") {
        // Another tab just logged in (or switched roles)
        if (myRole && msg.role && myRole !== msg.role) {
          // Different role took over -> disable this tab
          detachForRoleSwitch();
        } else {
          // Same role -> adopt latest token from LS if ours differs
          const lsToken = localStorage.getItem(TOKEN_KEY);
          if (lsToken && lsToken !== token) saveSession(lsToken);
        }
      }
      if (msg.type === "LOGOUT") {
        // Global logout from another tab -> clear here too
        clearInMemory();
      }
    };
    bcRef.current?.addEventListener("message", onMsg);
    return () => bcRef.current?.removeEventListener("message", onMsg);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, user]);

  // ---- Cross-tab sync: storage event (fires in other tabs)
  useEffect(() => {
    const onStorage = (e) => {
      if (!e) return;

      if (e.key === ROLE_KEY || e.key === TOKEN_KEY) {
        const lsToken = localStorage.getItem(TOKEN_KEY);
        const lsRole  = localStorage.getItem(ROLE_KEY);
        const myRole  = user ? (user.is_admin ? "admin" : "customer") : null;

        // Global logout in some tab
        if (!lsToken && !lsRole) {
          clearInMemory();
          return;
        }

        // Different role took over
        if (myRole && lsRole && myRole !== lsRole) {
          detachForRoleSwitch();
          return;
        }

        // Same role but token changed -> adopt it
        if (lsToken && lsToken !== token) {
          saveSession(lsToken);
        }
      }
    };

    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, user]);

  // ---- API
  const login = async (email, password) => {
    try {
      const { data } = await axios.post(`${API_BASE_URL}/api/customers/login`, { email, password });
      if (data.token) { saveSession(data.token); return { success: true }; }
      return { success: false, error: "Login failed" };
    } catch (error) {
      console.error("Login error:", error);
      return { success: false, error: error.response?.data?.detail || error.response?.data?.message || "Login failed" };
    }
  };

  const adminLogin = async (email, password) => {
    try {
      const { data } = await axios.post(`${API_BASE_URL}/api/customers/admin/login`, { email, password });
      if (data.token) { saveSession(data.token); return { success: true }; }
      return { success: false, error: "Admin login failed" };
    } catch (error) {
      console.error("Admin login error:", error);
      return { success: false, error: error.response?.data?.detail || error.response?.data?.message || "Admin login failed" };
    }
  };

  const register = async (userData) => {
    try {
      const { data } = await axios.post(`${API_BASE_URL}/api/customers/register`, userData);
      if (data.token) { saveSession(data.token); return { success: true }; }
      return { success: false, error: "Registration failed" };
    } catch (error) {
      console.error("Registration error:", error);
      return { success: false, error: error.response?.data?.detail || error.response?.data?.message || "Registration failed" };
    }
  };

  const value = useMemo(() => ({
      token,
      user,
      isRestoring,
      isAdmin: !!user?.is_admin,
      kickedByOtherRole,              // NEW: use in UI for a banner/toast
      login,
      adminLogin,
      register,
      logout,
    }),
    [token, user, isRestoring, kickedByOtherRole]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
