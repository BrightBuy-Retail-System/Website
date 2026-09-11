import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Hero from '../components/Hero.jsx';
import './HomePage.css';

function Home() {
    const [user, setUser] = useState(null);
    const navigate = useNavigate();

    const checkAuth = () => {
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
            try {
                setUser(JSON.parse(storedUser));
            } catch {
                setUser(null);
            }
        } else {
            setUser(null);
        }
    };

    useEffect(() => {
        checkAuth();
        window.addEventListener('storage', checkAuth);
        window.addEventListener('authChange', checkAuth);
        return () => {
            window.removeEventListener('storage', checkAuth);
            window.removeEventListener('authChange', checkAuth);
        };
    }, []);

    const handleLogout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        setUser(null);
        window.dispatchEvent(new Event('authChange'));
        navigate('/');
    };

    const userName = user ? (user.email ? user.email.split('@')[0] : 'Valued User') : '';

    return (
        <div className="home-container">
            {user ? (
                /* Authenticated User Dashboard View */
                <div className="dashboard-wrapper">
                    <header className="dashboard-header">
                        <div className="dashboard-badge">🚀 Active Session</div>
                        <h1 className="dashboard-title">
                            Dashboard of <span className="gradient-text">{userName}</span>
                        </h1>
                        <p className="dashboard-subtitle">
                            Welcome back to Bright Buy! Manage your account and explore bookings below.
                        </p>
                    </header>

                    <div className="dashboard-grid">
                        {/* Profile Summary Card */}
                        <div className="dashboard-card profile-card">
                            <div className="card-header">
                                <div className="user-icon-large">👤</div>
                                <div>
                                    <h3>User Profile</h3>
                                    <span className="status-pill active">● Active Member</span>
                                </div>
                            </div>
                            <div className="profile-details">
                                <div className="detail-row">
                                    <span className="detail-label">Email Address</span>
                                    <span className="detail-value">{user.email}</span>
                                </div>
                                <div className="detail-row">
                                    <span className="detail-label">Account ID</span>
                                    <span className="detail-value">#{user.id}</span>
                                </div>
                                <div className="detail-row">
                                    <span className="detail-label">Phone Number</span>
                                    <span className="detail-value">{user.phonenum || 'Not specified'}</span>
                                </div>
                            </div>
                            <button onClick={handleLogout} className="btn-dashboard-logout">
                                Sign Out
                            </button>
                        </div>

                        {/* Quick Actions Card */}
                        <div className="dashboard-card actions-card">
                            <div className="card-header">
                                <div className="user-icon-large">⚡</div>
                                <div>
                                    <h3>Quick Actions</h3>
                                    <span className="status-pill">Explore Services</span>
                                </div>
                            </div>
                            <div className="quick-actions-list">
                                <Link to="/products" className="action-item">
                                    <span className="action-icon">🛍️</span>
                                    <div className="action-text">
                                        <strong>Browse Products</strong>
                                        <span>Explore available items & inventory</span>
                                    </div>
                                    <span className="action-arrow">→</span>
                                </Link>
                                <Link to="/cart" className="action-item">
                                    <span className="action-icon">🛒</span>
                                    <div className="action-text">
                                        <strong>Shopping Cart</strong>
                                        <span>View items ready for checkout</span>
                                    </div>
                                    <span className="action-arrow">→</span>
                                </Link>
                                <Link to="/orders" className="action-item">
                                    <span className="action-icon">📦</span>
                                    <div className="action-text">
                                        <strong>Booking & Orders</strong>
                                        <span>Track real-time delivery and schedules</span>
                                    </div>
                                    <span className="action-arrow">→</span>
                                </Link>
                            </div>
                        </div>
                    </div>
                </div>
            ) : (
                /* Guest Landing Page View */
                <>
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
                </>
            )}
        </div>
    );
}

export default Home;