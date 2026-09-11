import { useState, useEffect } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import './Navbar.css';

function Navbar() {
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

    return (
        <header className="navbar">
            {/* Logo */}
            <div className="navbar-logo">
                <Link to="/">
                    <span className="logo-icon">🛍️</span>
                    <span className="logo-text">Bright Buy</span>
                </Link>
            </div>

            {/* Nav Links */}
            <nav className="navbar-links">
                <NavLink
                    to="/"
                    className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
                >
                    Home
                </NavLink>

                <NavLink
                    to="/products"
                    className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
                >
                    Products
                </NavLink>

                <NavLink
                    to="/cart"
                    className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
                >
                    Cart
                </NavLink>

                <NavLink
                    to="/orders"
                    className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
                >
                    Orders
                </NavLink>
            </nav>

            {/* Auth Actions */}
            <div className="navbar-actions">
                {user ? (
                    <div className="user-profile-badge">
                        <span className="user-avatar-icon">👤</span>
                        <span className="user-email-tag" title={user.email}>
                            {user.email.split('@')[0]}
                        </span>
                        <button onClick={handleLogout} className="btn-logout" title="Sign Out">
                            Sign Out
                        </button>
                    </div>
                ) : (
                    <div className="guest-actions">
                        <Link to="/login" className="btn-secondary">
                            Login
                        </Link>
                        <Link to="/register" className="btn-primary">
                            Register
                        </Link>
                    </div>
                )}
            </div>
        </header>
    );
}

export default Navbar;