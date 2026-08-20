import { useState } from 'react'
import { Routes, Route } from 'react-router-dom';
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import heroImg from './assets/hero.png'
import Hero from './Hero.jsx'
import './App.css'
import LoginPage from './login.jsx';
import RegisterPage from './Register.jsx'

function App() {
  return (
    <Routes>
      <Route path= "/" element={<Hero />} />
      <Route path= "/login" element={<LoginPage />} />
      <Route path= "/Register" element={<RegisterPage />} />
    </Routes>
  );
}

export default App;
