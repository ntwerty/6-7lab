import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './Home.css';

const Home = () => {
  const { isAuthenticated } = useAuth();

  return (
    <div className="home">
      <div className="hero">
        <h1 className="hero-title">🎮 Арканоид</h1>
        <p className="hero-subtitle">Классическая игра с современными возможностями</p>
        {isAuthenticated ? (
          <Link to="/game" className="btn btn-primary btn-large">
            Начать игру
          </Link>
        ) : (
          <div className="hero-actions">
            <Link to="/register" className="btn btn-primary btn-large">
              Начать игру
            </Link>
            <Link to="/login" className="btn btn-secondary btn-large">
              Войти
            </Link>
          </div>
        )}
      </div>

      <div className="features">
        <div className="feature-card">
          <div className="feature-icon">🏆</div>
          <h3>Таблица лидеров</h3>
          <p>Соревнуйтесь с другими игроками и займите первое место!</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">🎯</div>
          <h3>Достижения</h3>
          <p>Получайте достижения за ваши успехи в игре</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">👥</div>
          <h3>Друзья</h3>
          <p>Добавляйте друзей и бросайте им вызовы</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">💾</div>
          <h3>Сохранение прогресса</h3>
          <p>Ваш прогресс автоматически сохраняется</p>
        </div>
      </div>
    </div>
  );
};

export default Home;

