import {Link} from 'react-router';

function Hero(){
    return (
        <div className = 'Hero'>
            <h1>Bright Buy Retail System</h1>
            <Link to="/login" className="btn">Login</Link>
            <Link to="/Register" className="btn">Register</Link>
        </div>
    );
}

export default Hero;