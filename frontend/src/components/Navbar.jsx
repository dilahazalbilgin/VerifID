import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import styles from '../styles/Navbar.module.scss';
import logo from '../assets/logo.png';

function Navbar() {
  const { user, logout, isVerified } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  // Function to handle hash links
  const handleHashLink = (e, hash) => {
    e.preventDefault();
    
    // If we're already on the home page, just scroll to the section
    if (location.pathname === '/') {
      const element = document.querySelector(hash);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
      }
    } else {
      // If we're on another page, navigate to home with the hash
      navigate('/' + hash);
    }
  };

  return (
    <nav className={styles.navbar}>
      <div className={styles.navbarLeft}>
        <Link to="/" className={styles.logo}>
          <img src={logo} alt="Logo" />
          <span className={styles.companyName}>VerifID</span>
        </Link>
      </div>
      
      <div className={styles.navbarCenter}>
        <ul className={styles.navLinks}>
          {user ? (
            // Navigation links for logged-in users
            <>
              <li><Link to="/">Home</Link></li>
              {!isVerified() && (
                <li>
                  <Link to="/verify" className={styles.verifyLink}>
                    Verify
                  </Link>
                </li>
              )}
              <li><Link to="/profile">Profile</Link></li>
            </>
          ) : (
            // Navigation links for guests
            <>
              <li>
                <a 
                  href="#about" 
                  onClick={(e) => handleHashLink(e, '#about')}
                >
                  About
                </a>
              </li>
              <li>
                <a 
                  href="#how-it-works" 
                  onClick={(e) => handleHashLink(e, '#how-it-works')}
                >
                  How It Works
                </a>
              </li>
              <li>
                <a 
                  href="#contact" 
                  onClick={(e) => handleHashLink(e, '#contact')}
                >
                  Contact
                </a>
              </li>
            </>
          )}
        </ul>
      </div>
      
      <div className={styles.navbarRight}>
        {user ? (
          <>
            <Link to="/profile" className={styles.profileBtn}>
              Profile
            </Link>
            <Link to="/" className={styles.logoutBtn} onClick={handleLogout}>
              Logout
           </Link>
          </>
        ) : (
          <>
            <Link to="/login" className={styles.loginBtn}>
              Login
            </Link>
            <Link to="/register" className={styles.registerBtn}>
              Register
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}

export default Navbar;




