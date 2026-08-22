import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./Auth.css";

function RegisterPage() {
    const navigate = useNavigate();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const [phonenum, setPhonenum] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);


    const handlesubmit = async (e) => {
        e.preventDefault();
        setError("");
        setLoading(true);

        try {

            const response = await fetch("http://localhost:8000/api/register", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password, phonenum }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || "Registration faild");
            }

            alert("Registration successful! Please login.");

            navigate("/login");

        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                <header className="auth-header">
                    <h1>Create Account</h1>
                    <p>Welcome to Bright Buy Retail System</p>
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
                                    placeholder="Create a strong password"
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

                        {/* Phone Number Field */}
                        <div className="form-group">
                            <label htmlFor="phonenum">Phone Number</label>
                            <div className="input-wrapper">
                                <input
                                    type="tel"
                                    id="phonenum"
                                    value={phonenum}
                                    onChange={(e) => setPhonenum(e.target.value)}
                                    placeholder="Enter your phone number"
                                />
                            </div>
                        </div>

                        <button type="submit" className="auth-submit-btn">
                            Register
                        </button>
                    </form>
                </main>

                <footer className="auth-footer">
                    <p>
                        Already have an account?
                        <Link to="/login">Login here</Link>
                    </p>
                </footer>
            </div>
        </div>
    );
}

export default RegisterPage;
