// context/AuthContext.tsx
'use client';
import React, { createContext, useEffect, useState, ReactNode } from 'react';

interface AuthContextProps {
  isAuthenticated: boolean;
  loading: boolean;
}

export const AuthContext = createContext<AuthContextProps>({
  isAuthenticated: false,
  loading: true,
});

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Validate authentication by calling FastAPI's /api/validate endpoint.
    fetch('http://localhost:8000/api/validate', {
      credentials: 'include', // Sends HTTP-only cookie along with the request.
    })
      .then((res) => {
        if (res.ok) return res.json();
        throw new Error('Not authenticated');
      })
      .then((data) => {
        setIsAuthenticated(data.authenticated);
        setLoading(false);
      })
      .catch(() => {
        setIsAuthenticated(false);
        setLoading(false);
      });
  }, []);

  return (
    <AuthContext.Provider value={{ isAuthenticated, loading }}>
      {children}
    </AuthContext.Provider>
  );
};
