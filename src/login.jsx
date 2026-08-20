import {useState} from "react";

function LoginPage(){
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);

    const handlesubmit = (e) => {
        e.preventDefault();
        console.log("Logging in with:", {email, password});
    };

    return (
        <div>

            <header>
                <h1>Welcome Back </h1>
                <p>Please Login to your account</p>
            </header>

            <main>
                <form onSubmit={handlesubmit}>
                    {/*Email feild*/}
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

                    {/*Password Feild*/}
                    <div>
                        <label htmlFor="Password">Password</label>
                        <input
                            type="password"
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

                    {/*Actions*/}
                    <div>
                        <a href="/forgot-password">Forgot password ??🥲</a>
                    </div>

                    <button type="submit">➡️</button>
                </form>
            </main>

            <footer>
                <p>
                    Don't have an account? How sad🤦 <a href="/register">Try Register</a>
                </p>
            </footer>
        </div>
    );
}

export default LoginPage;