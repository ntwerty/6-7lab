import React, { useState, useEffect } from 'react';
import api from '../services/api';
import './Achievements.css';

const Achievements = () => {
  const [allAchievements, setAllAchievements] = useState([]);
  const [userAchievements, setUserAchievements] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAchievements();
  }, []);

  const loadAchievements = async () => {
    try {
      const [allRes, userRes] = await Promise.all([
        api.get('/achievements/'),
        api.get('/user-achievements/my_achievements/')
      ]);
      
      setAllAchievements(allRes.data.results || allRes.data || []);
      setUserAchievements(userRes.data || []);
    } catch (error) {
      console.error('Ошибка загрузки достижений:', error);
    } finally {
      setLoading(false);
    }
  };

  const isUnlocked = (achievementId) => {
    return userAchievements.some(ua => ua.achievement.id === achievementId);
  };

  if (loading) {
    return <div className="loading"><div className="spinner"></div></div>;
  }

  const unlockedCount = userAchievements.length;
  const totalCount = allAchievements.length;

  return (
    <div className="achievements-page">
      <div className="card">
        <h2>Достижения</h2>
        <div className="achievements-progress">
          <p>
            Разблокировано: <strong>{unlockedCount} / {totalCount}</strong>
          </p>
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${(unlockedCount / totalCount) * 100}%` }}
            ></div>
          </div>
        </div>

        <div className="achievements-grid">
          {allAchievements.map((achievement) => {
            const unlocked = isUnlocked(achievement.id);
            return (
              <div
                key={achievement.id}
                className={`achievement-card ${unlocked ? 'unlocked' : 'locked'}`}
              >
                <div className="achievement-icon">
                  {unlocked ? '🏆' : '🔒'}
                </div>
                <h3>{achievement.name}</h3>
                <p>{achievement.description}</p>
                <div className="achievement-requirements">
                  <span>Очков: {achievement.points_required}</span>
                  <span>Уровень: {achievement.level_required}</span>
                </div>
                {unlocked && (
                  <div className="achievement-date">
                    Получено: {new Date(
                      userAchievements.find(ua => ua.achievement.id === achievement.id)?.unlocked_at
                    ).toLocaleDateString('ru-RU')}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default Achievements;

