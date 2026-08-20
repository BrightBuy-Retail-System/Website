import { useState } from "react";

function RegisterPage() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const [phonenum, setPhonenum] = useState(""); // Lowercase 'p'

    const handlesubmit = (e) => {
        e.preventDefault();
        // Updated console log to include the phone number
        console.log("Registering in with:", { email, password, phonenum });
    };

    return (
        <div>
            <header>
                <h1>Welcome to Bright Buy Retail System</h1>
            </header>

            <main>
                <form onSubmit={handlesubmit}>
                    {/* Email field */}
                    <div>
                        <label htmlFor="email">Email Address</label>
                        <input
                            type="email"
                            id="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="name@example.com"
                            required
                        />
                    </div>

                    {/* Password Field */}
                    <div>
                        <label htmlFor="password">Password</label>
                        <input
                            type={showPassword ? "text" : "password"} // Fixed visibility toggle
                            id="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Enter your password"
                            required
                        />
                        <button 
                            type="button"
                            onClick={() => setShowPassword(!showPassword)}
                        >
                            {showPassword ? "Hide" : "Show"}
                        </button>
                    </div>

                    {/* Phone Number Field */}
                    <div>
                        <label htmlFor="Phonenum">Phone Number</label> {/* Fixed htmlFor */}
                        <input
                            type="tel" // Fixed input type
                            id="Phonenum"
                            value={phonenum} // Fixed casing to lowercase 'p'
                            onChange={(e) => setPhonenum(e.target.value)}
                            placeholder="Enter your phone number" 
                        />
                    </div>

                    <button type="submit">➡️</button>
                </form>
            </main>

            <footer>
                <p>
                    Already have an account? Happy Happy Happy .. 😸 <a href="/login">Login here</a>
                </p>
            </footer>
        </div>
    );
}

export default RegisterPage;
