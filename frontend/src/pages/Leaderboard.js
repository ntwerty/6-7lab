import React, { useState, useEffect } from 'react';
import api from '../services/api';
import './Leaderboard.css';

const Leaderboard = () => {
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);
  const [difficulty, setDifficulty] = useState('medium');
  const [topPlayers, setTopPlayers] = useState([]);

  useEffect(() => {
    loadLeaderboard();
    loadTopPlayers();
  }, [difficulty]);

  const loadLeaderboard = async () => {
    try {
      const response = await api.get(`/leaderboard/?difficulty=${difficulty}&ordering=-score`);
      setLeaderboard(response.data.results || []);
    } catch (error) {
      console.error('Ошибка загрузки таблицы лидеров:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadTopPlayers = async () => {
    try {
      const response = await api.get(`/leaderboard/top/?limit=10&difficulty=${difficulty}`);
      setTopPlayers(response.data || []);
    } catch (error) {
      console.error('Ошибка загрузки топ игроков:', error);
    }
  };

  if (loading) {
    return <div className="loading"><div className="spinner"></div></div>;
  }

  return (
    <div className="leaderboard-page">
      <div className="card">
        <h2>Таблица лидеров</h2>
        <div className="form-group" style={{ maxWidth: '300px' }}>
          <label htmlFor="difficulty">Сложность:</label>
          <select
            id="difficulty"
            value={difficulty}
            onChange={(e) => setDifficulty(e.target.value)}
            className="form-group select"
          >
            <option value="easy">Легкий</option>
            <option value="medium">Средний</option>
            <option value="hard">Сложный</option>
          </select>
        </div>

        <div className="top-players">
          <h3>Топ 10 игроков</h3>
          <div className="leaderboard-table">
            <div className="leaderboard-header">
              <div>Ранг</div>
              <div>Игрок</div>
              <div>Счет</div>
              <div>Дата</div>
            </div>
            {topPlayers.map((entry, index) => (
              <div key={entry.id} className="leaderboard-row">
                <div className="rank">#{entry.rank || index + 1}</div>
                <div className="username">{entry.username}</div>
                <div className="score">{entry.score}</div>
                <div className="date">
                  {new Date(entry.date_achieved).toLocaleDateString('ru-RU')}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="all-players">
          <h3>Все игроки</h3>
          <div className="leaderboard-table">
            <div className="leaderboard-header">
              <div>Ранг</div>
              <div>Игрок</div>
              <div>Счет</div>
              <div>Дата</div>
            </div>
            {leaderboard.length > 0 ? (
              leaderboard.map((entry) => (
                <div key={entry.id} className="leaderboard-row">
                  <div className="rank">#{entry.rank}</div>
                  <div className="username">{entry.username}</div>
                  <div className="score">{entry.score}</div>
                  <div className="date">
                    {new Date(entry.date_achieved).toLocaleDateString('ru-RU')}
                  </div>
                </div>
              ))
            ) : (
              <div className="leaderboard-row">
                <div colSpan="4" style={{ textAlign: 'center', padding: '20px' }}>
                  Нет записей
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Leaderboard;

