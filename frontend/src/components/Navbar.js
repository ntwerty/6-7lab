import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './Navbar.css';

const Navbar = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          🎮 Арканоид
        </Link>
        <div className="navbar-menu">
          {isAuthenticated ? (
            <>
              <Link to="/game" className="navbar-link">Играть</Link>
              <Link to="/leaderboard" className="navbar-link">Лидеры</Link>
              <Link to="/achievements" className="navbar-link">Достижения</Link>
              <Link to="/friends" className="navbar-link">Друзья</Link>
              <Link to="/profile" className="navbar-link">
                {user?.username || 'Профиль'}
              </Link>
              <button onClick={handleLogout} className="navbar-link btn-logout">
                Выход
              </button>
            </>
          ) : (
            <>
              <Link to="/leaderboard" className="navbar-link">Лидеры</Link>
              <Link to="/login" className="navbar-link">Вход</Link>
              <Link to="/register" className="navbar-link btn-register">
                Регистрация
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;

