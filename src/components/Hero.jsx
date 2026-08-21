import { Link } from 'react-router-dom';
import heroImg from '../assets/hero.png';

function Hero() {
    return (
        <section className="hero-section">
            <div className="hero-content">
                {/* Left Column: Heading & CTAs */}
                <div className="hero-text">
                    <div className="hero-badge">
                        <span>✨</span> Smart Retail & Booking Platform
                    </div>
                    <h1 className="hero-title">
                        Empower Your Shopping with <span className="gradient-text">Bright Buy</span>
                    </h1>
                    <p className="hero-description">
                        Explore quality products, manage your retail bookings, and experience effortless order tracking all in one seamless place.
                    </p>
                    <div className="hero-actions">
                        <Link to="/register" className="hero-btn-primary">
                            Get Started 🚀
                        </Link>
                        <Link to="/login" className="hero-btn-secondary">
                            Sign In 👤
                        </Link>
                    </div>
                </div>

                {/* Right Column: Visual Showcase */}
                <div className="hero-image-wrapper">
                    <div className="hero-img-card">
                        <img 
                            src={heroImg} 
                            alt="Bright Buy Retail System Showcase" 
                            className="hero-main-img" 
                        />
                        <div className="floating-badge">
                            <span className="floating-badge-icon">🛍️</span>
                            <div className="floating-badge-text">
                                <strong>Fast & Easy</strong>
                                <span>Seamless Bookings</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}

export default Hero;