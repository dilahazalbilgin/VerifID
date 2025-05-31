import React from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import styles from '../styles/NotFound.module.scss';

function NotFound() {
  return (
    <div className={styles.pageContainer}>
      <Navbar />
      <div className={styles.notFoundContainer}>
        <h1>404</h1>
        <h2>Page Not Found</h2>
        <p>The page you are looking for doesn't exist or has been moved.</p>
        <Link to="/" className={styles.homeButton}>
          Go to Home
        </Link>
      </div>
    </div>
  );
}

export default NotFound;