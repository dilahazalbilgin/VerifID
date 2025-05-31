import React, { useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import styles from '../../styles/HomePage.module.scss';
import Navbar from '../../components/Navbar';

function HomePage() {
  const location = useLocation();
  const navigate = useNavigate();

  // Handle hash navigation when coming from another page
  useEffect(() => {
    if (location.hash) {
      // Wait a bit for the DOM to fully render
      setTimeout(() => {
        const element = document.querySelector(location.hash);
        if (element) {
          element.scrollIntoView({ behavior: 'smooth' });
        }
      }, 100);
    } else {
      // Scroll to top when navigating to home without hash
      window.scrollTo(0, 0);
    }
  }, [location]);

  // Function to handle the "Get Started" button click
  const handleGetStarted = () => {
    navigate('/login');
  };

  return (
    <div className={styles.pageContainer}>
      <Navbar />
      <div className={styles.homeContainer}>
        <section className={styles.heroSection}>
          <h1>Secure Identity Verification</h1>
          <p>Fast, reliable, and secure identity verification for businesses and individuals</p>
          <button 
            className={styles.ctaButton}
            onClick={handleGetStarted}
          >
            Get Started
          </button>
        </section>
        
        <section id="about" className={styles.aboutSection}>
          <h2>About VerifID</h2>
          <p>
            VerifID is a cutting-edge identity verification platform that helps businesses 
            and individuals verify identities securely and efficiently. Our advanced 
            technology ensures the highest level of security while maintaining ease of use.
          </p>
          <p>
            With our state-of-the-art facial recognition and document verification systems,
            we provide a seamless verification experience that is both fast and reliable.
            Our platform is designed to meet the needs of various industries, including
            finance, healthcare, and e-commerce.
          </p>
        </section>
        
        <section id="how-it-works" className={styles.howItWorksSection}>
          <h2>How It Works</h2>
          <div className={styles.stepsContainer}>
            <div className={styles.step}>
              <div className={styles.stepNumber}>1</div>
              <h3>Create an Account</h3>
              <p>Sign up for a VerifID account with your basic information</p>
            </div>
            
            <div className={styles.step}>
              <div className={styles.stepNumber}>2</div>
              <h3>Upload Documents</h3>
              <p>Upload your identification documents for verification</p>
            </div>
            
            <div className={styles.step}>
              <div className={styles.stepNumber}>3</div>
              <h3>Verify Identity</h3>
              <p>Complete a quick facial recognition check to confirm your identity</p>
            </div>
          </div>
        </section>
        
        <section id="contact" className={styles.contactSection}>
          <h2>Contact Us</h2>
          <p>Have questions or need assistance? Reach out to our team.</p>
          
          <div className={styles.contactOptions}>
            <div className={styles.contactMethod}>
              <div className={styles.contactIcon}>
                <i className="far fa-envelope"></i>
              </div>
              <h3>Email</h3>
              <p>support@verifid.com</p>
              <a href="mailto:support@verifid.com" className={styles.contactLink}>Send an email</a>
            </div>
            
            <div className={styles.contactMethod}>
              <div className={styles.contactIcon}>
                <i className="fab fa-instagram"></i>
              </div>
              <h3>Instagram</h3>
              <p>@verifid_official</p>
              <a href="https://instagram.com/verifid_official" target="_blank" rel="noopener noreferrer" className={styles.contactLink}>Follow us</a>
            </div>
            
            <div className={styles.contactMethod}>
              <div className={styles.contactIcon}>
                <i className="fab fa-twitter"></i>
              </div>
              <h3>Twitter</h3>
              <p>@VerifID</p>
              <a href="https://twitter.com/VerifID" target="_blank" rel="noopener noreferrer" className={styles.contactLink}>Tweet us</a>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

export default HomePage;
