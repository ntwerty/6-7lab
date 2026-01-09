import React, { useState, useEffect } from 'react';
import api from '../services/api';
import './Friends.css';

const Friends = () => {
  const [friends, setFriends] = useState([]);
  const [pendingRequests, setPendingRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [username, setUsername] = useState('');
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadFriends();
    loadPendingRequests();
  }, []);

  const loadFriends = async () => {
    try {
      const response = await api.get('/friends/my_friends/');
      setFriends(response.data || []);
    } catch (error) {
      console.error('Ошибка загрузки друзей:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadPendingRequests = async () => {
    try {
      const response = await api.get('/friends/');
      const all = response.data.results || response.data || [];
      setPendingRequests(all.filter(f => f.status === 'pending'));
    } catch (error) {
      console.error('Ошибка загрузки запросов:', error);
    }
  };

  const handleAddFriend = async (e) => {
    e.preventDefault();
    if (!username.trim()) return;

    try {
      await api.post('/friends/', { to_username: username });
      setMessage('Запрос отправлен!');
      setUsername('');
      setTimeout(() => setMessage(''), 3000);
      loadPendingRequests();
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Ошибка отправки запроса');
      setTimeout(() => setMessage(''), 3000);
    }
  };

  const handleAccept = async (id) => {
    try {
      await api.post(`/friends/${id}/accept/`);
      loadFriends();
      loadPendingRequests();
      setMessage('Запрос принят!');
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage('Ошибка принятия запроса');
      setTimeout(() => setMessage(''), 3000);
    }
  };

  const handleReject = async (id) => {
    try {
      await api.post(`/friends/${id}/reject/`);
      loadPendingRequests();
    } catch (error) {
      console.error('Ошибка отклонения запроса:', error);
    }
  };

  if (loading) {
    return <div className="loading"><div className="spinner"></div></div>;
  }

  return (
    <div className="friends-page">
      <div className="card">
        <h2>Друзья</h2>
        {message && (
          <div className={message.includes('Ошибка') ? 'error-message' : 'success-message'}>
            {message}
          </div>
        )}

        <div className="add-friend-section">
          <h3>Добавить друга</h3>
          <form onSubmit={handleAddFriend} style={{ display: 'flex', gap: '10px' }}>
            <input
              type="text"
              placeholder="Имя пользователя"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="form-group input"
              style={{ flex: 1 }}
            />
            <button type="submit" className="btn btn-primary">
              Отправить запрос
            </button>
          </form>
        </div>

        {pendingRequests.length > 0 && (
          <div className="pending-requests">
            <h3>Ожидающие запросы</h3>
            {pendingRequests.map((request) => (
              <div key={request.id} className="friend-item">
                <span>{request.from_username}</span>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <button
                    onClick={() => handleAccept(request.id)}
                    className="btn btn-success"
                    style={{ padding: '8px 16px' }}
                  >
                    Принять
                  </button>
                  <button
                    onClick={() => handleReject(request.id)}
                    className="btn btn-danger"
                    style={{ padding: '8px 16px' }}
                  >
                    Отклонить
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="friends-list">
          <h3>Мои друзья ({friends.length})</h3>
          {friends.length > 0 ? (
            <div className="friends-grid">
              {friends.map((friend) => {
                const friendUsername = friend.from_username === friend.to_username 
                  ? friend.to_username 
                  : friend.from_username;
                return (
                  <div key={friend.id} className="friend-card">
                    <div className="friend-avatar">👤</div>
                    <div className="friend-name">{friendUsername}</div>
                  </div>
                );
              })}
            </div>
          ) : (
            <p>У вас пока нет друзей</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Friends;

