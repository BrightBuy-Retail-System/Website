import { useState } from "react";
import { Link } from "react-router-dom";
import "./Auth.css";

function LoginPage() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);

    const handlesubmit = (e) => {
        e.preventDefault();
        console.log("Logging in with:", { email, password });
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                <header className="auth-header">
                    <h1>Welcome Back</h1>
                    <p>Please login to your account</p>
                </header>

                <main>
                    <form onSubmit={handlesubmit} className="auth-form">
                        {/* Email field */}
                        <div className="form-group">
                            <label htmlFor="email">Email Address</label>
                            <div className="input-wrapper">
                                <input
                                    type="email"
                                    id="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    placeholder="name@example.com"
                                    required
                                />
                            </div>
                        </div>

                        {/* Password Field */}
                        <div className="form-group">
                            <label htmlFor="password">Password</label>
                            <div className="input-wrapper">
                                <input
                                    type={showPassword ? "text" : "password"}
                                    id="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder="Enter your password"
                                    required
                                />
                                <button 
                                    type="button"
                                    className="password-toggle-btn"
                                    onClick={() => setShowPassword(!showPassword)}
                                >
                                    {showPassword ? "Hide" : "Show"}
                                </button>
                            </div>
                        </div>

                        {/* Actions */}
                        <div className="auth-actions">
                            <Link to="/forgot-password" className="forgot-password-link">
                                Forgot password?
                            </Link>
                        </div>

                        <button type="submit" className="auth-submit-btn">
                            Login
                        </button>
                    </form>
                </main>

                <footer className="auth-footer">
                    <p>
                        Don't have an account? 
                        <Link to="/register">Create an account</Link>
                    </p>
                </footer>
            </div>
        </div>
    );
}

export default LoginPage;