import React, { createContext, useState, useContext, useEffect } from 'react';

// Create the context
const AuthContext = createContext(null);

// Custom hook for using the auth context
export function useAuth() {
  return useContext(AuthContext);
}

// Provider component
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Check if user is logged in from localStorage
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    setError(null);
    try {
      const response = await fetch('http://localhost:5000/api/users/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Login failed');
      }
      
      const userData = {
        id: data._id,
        firstName: data.firstName,
        lastName: data.lastName,
        email: data.email,
        idCardNumber: data.idCardNumber || '',
        birthDate: data.birthDate || '',
        serialNumber: data.serialNumber || '',
        gender: data.gender || '',
        isVerified: data.isVerified,
        token: data.token
      };
      
      console.log("Login response data:", data); // Debug log
      console.log("Processed user data:", userData); // Debug log
      
      setUser(userData);
      localStorage.setItem('user', JSON.stringify(userData));
      return userData;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const register = async (userData) => {
    setError(null);
    try {
      const response = await fetch('http://localhost:5000/api/users', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Registration failed');
      }
      
      console.log("Register response data:", data); // Debug log
      
      // Don't set user or store in localStorage
      // Just return the data
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('user');
  };

  const isVerified = () => {
    return user && user.isVerified;
  };

  const updateProfile = async (userData) => {
    setError(null);
    try {
      console.log("Sending update data:", userData); // Debug log
      
      const response = await fetch('http://localhost:5000/api/users/profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user.token}`
        },
        body: JSON.stringify(userData),
      });

      const data = await response.json();
      
      console.log("Update response data:", data); // Debug log
      
      if (!response.ok) {
        throw new Error(data.message || 'Profile update failed');
      }
      
      // Preserve existing user data and merge with updated data
      const updatedUser = {
        ...user,
        id: data._id || user.id,
        firstName: data.firstName || user.firstName,
        lastName: data.lastName || user.lastName,
        email: data.email || user.email,
        idCardNumber: data.idCardNumber || user.idCardNumber,
        birthDate: data.birthDate || user.birthDate,
        serialNumber: data.serialNumber || user.serialNumber,
        gender: data.gender || user.gender,
        isVerified: data.isVerified !== undefined ? data.isVerified : user.isVerified,
        token: data.token || user.token
      };
      
      console.log("Processed updated user data:", updatedUser); // Debug log
      
      setUser(updatedUser);
      localStorage.setItem('user', JSON.stringify(updatedUser));
      return updatedUser;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  // Create the context value object
  const contextValue = {
    user, 
    login, 
    logout, 
    register,
    updateProfile,
    loading, 
    isVerified,
    error 
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}





