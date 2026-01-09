import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import './Profile.css';

const Profile = () => {
  const { user, isAuthenticated } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({
    bio: '',
    date_of_birth: ''
  });
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const response = await api.get('/profiles/me/');
      setProfile(response.data);
      setFormData({
        bio: response.data.bio || '',
        date_of_birth: response.data.date_of_birth || ''
      });
    } catch (error) {
      console.error('Ошибка загрузки профиля:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.patch(`/profiles/${profile.id}/`, formData);
      await loadProfile();
      setEditing(false);
      setMessage('Профиль обновлен!');
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage('Ошибка обновления профиля');
      console.error(error);
    }
  };

  if (loading) {
    return <div className="loading"><div className="spinner"></div></div>;
  }

  if (!profile) {
    return <div className="card"><p>Профиль не найден</p></div>;
  }

  return (
    <div className="profile-page">
      <div className="card">
        <h2>Мой профиль</h2>
        {message && <div className={message.includes('Ошибка') ? 'error-message' : 'success-message'}>{message}</div>}
        
        {!editing ? (
          <div className="profile-view">
            <div className="profile-info">
              <p><strong>Имя пользователя:</strong> {profile.username}</p>
              <p><strong>Email:</strong> {profile.user?.email || 'Не указан'}</p>
              <p><strong>Биография:</strong> {profile.bio || 'Не указана'}</p>
              <p><strong>Дата рождения:</strong> {profile.date_of_birth || 'Не указана'}</p>
              <p><strong>Общий счет:</strong> {profile.total_score}</p>
              <p><strong>Игр сыграно:</strong> {profile.games_played}</p>
            </div>
            <button onClick={() => setEditing(true)} className="btn btn-primary">
              Редактировать
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="bio">Биография</label>
              <textarea
                id="bio"
                value={formData.bio}
                onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                rows="4"
              />
            </div>
            <div className="form-group">
              <label htmlFor="date_of_birth">Дата рождения</label>
              <input
                type="date"
                id="date_of_birth"
                value={formData.date_of_birth}
                onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })}
              />
            </div>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button type="submit" className="btn btn-primary">
                Сохранить
              </button>
              <button
                type="button"
                onClick={() => {
                  setEditing(false);
                  loadProfile();
                }}
                className="btn btn-secondary"
              >
                Отмена
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};

export default Profile;

