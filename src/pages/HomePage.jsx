import Hero from '../components/Hero.jsx';
import './HomePage.css';

function Home() {
    return (
        <div className="home-container">
            {/* Hero Banner Component */}
            <Hero />

            {/* Feature Highlights Section */}
            <section className="features-section">
                <div className="features-header">
                    <h2>Why Choose Bright Buy?</h2>
                    <p>Designed to deliver the fastest and smoothest shopping & retail experience.</p>
                </div>

                <div className="features-grid">
                    <div className="feature-card">
                        <div className="feature-icon">⚡</div>
                        <h3>Instant Booking</h3>
                        <p>Reserve and schedule product bookings in seconds with real-time confirmation.</p>
                    </div>

                    <div className="feature-card">
                        <div className="feature-icon">🔒</div>
                        <h3>Secure & Reliable</h3>
                        <p>Your transactions and personal account data are guarded with industry-standard encryption.</p>
                    </div>

                    <div className="feature-card">
                        <div className="feature-icon">📦</div>
                        <h3>Real-Time Tracking</h3>
                        <p>Track your orders, order history, and booking status effortlessly from your dashboard.</p>
                    </div>
                </div>
            </section>
        </div>
    );
}

export default Home;