import { Link, NavLink } from 'react-router-dom';
import './Navbar.css';

function Navbar() {
    return (
        <header className="navbar">
            {/*logo*/}
            <div className="navbar-logo">
                <Link to="/">
                    <span className="logo-icon"></span>
                    <span className="logo-text">Bright Buy</span>
                </Link>
            </div>

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
        </header>
    )
}

export default Navbar;