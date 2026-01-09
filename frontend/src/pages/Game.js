import React, { useRef, useEffect, useState, useCallback } from 'react';
import api from '../services/api';
import './Game.css';

const Game = () => {
  const canvasRef = useRef(null);
  const [gameState, setGameState] = useState(null);
  const [score, setScore] = useState(0);
  const [level, setLevel] = useState(1);
  const [lives, setLives] = useState(3);
  const [gameOver, setGameOver] = useState(false);
  const [paused, setPaused] = useState(false);
  const [difficulty, setDifficulty] = useState('medium');
  const [timePlayed, setTimePlayed] = useState(0);
  const [saving, setSaving] = useState(false);
  
  const gameLoopRef = useRef(null);
  const startTimeRef = useRef(Date.now());

  // Игровые объекты
  const paddleRef = useRef({ x: 0, width: 100, speed: 8 });
  const ballRef = useRef({ x: 0, y: 0, vx: 0, vy: 0, radius: 8 });
  const blocksRef = useRef([]);
  const keysRef = useRef({ left: false, right: false });

  // Инициализация игры
  const initGame = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    canvas.width = 800;
    canvas.height = 600;

    // Платформа
    paddleRef.current = {
      x: canvas.width / 2 - 50,
      width: 100,
      speed: difficulty === 'easy' ? 10 : difficulty === 'hard' ? 6 : 8
    };

    // Шарик
    ballRef.current = {
      x: canvas.width / 2,
      y: canvas.height - 50,
      vx: difficulty === 'easy' ? 4 : difficulty === 'hard' ? 6 : 5,
      vy: -(difficulty === 'easy' ? 4 : difficulty === 'hard' ? 6 : 5),
      radius: 8
    };

    // Блоки
    blocksRef.current = [];
    const rows = difficulty === 'easy' ? 3 : difficulty === 'hard' ? 6 : 4;
    const cols = 10;
    const blockWidth = 70;
    const blockHeight = 30;
    const blockPadding = 5;
    const offsetTop = 50;
    const offsetLeft = (canvas.width - (cols * (blockWidth + blockPadding) - blockPadding)) / 2;

    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        blocksRef.current.push({
          x: offsetLeft + c * (blockWidth + blockPadding),
          y: offsetTop + r * (blockHeight + blockPadding),
          width: blockWidth,
          height: blockHeight,
          destroyed: false,
          color: `hsl(${r * 30}, 70%, 50%)`
        });
      }
    }

    setScore(0);
    setLives(3);
    setGameOver(false);
    setPaused(false);
    startTimeRef.current = Date.now();
  }, [difficulty]);

  // Загрузка сохранения
  const loadGame = useCallback(async () => {
    try {
      const response = await api.get('/game-sessions/latest/');
      const data = response.data;
      
      if (data && data.game_state) {
        const state = data.game_state;
        paddleRef.current = state.paddle || paddleRef.current;
        ballRef.current = state.ball || ballRef.current;
        blocksRef.current = state.blocks || blocksRef.current;
        setScore(data.score || 0);
        setLevel(data.level || 1);
        setLives(state.lives || 3);
        setDifficulty(data.difficulty || 'medium');
        setTimePlayed(data.time_played || 0);
        
        const canvas = canvasRef.current;
        if (canvas) {
          canvas.width = 800;
          canvas.height = 600;
        }
      } else {
        initGame();
      }
    } catch (error) {
      console.error('Ошибка загрузки:', error);
      initGame();
    }
  }, [initGame]);

  // Сохранение игры
  const saveGame = useCallback(async (completed = false) => {
    if (saving) return;
    
    setSaving(true);
    try {
      const gameState = {
        paddle: paddleRef.current,
        ball: ballRef.current,
        blocks: blocksRef.current,
        lives
      };

      const timePlayedSeconds = Math.floor((Date.now() - startTimeRef.current) / 1000) + timePlayed;

      await api.post('/game-sessions/', {
        game_state: gameState,
        score,
        level,
        time_played: timePlayedSeconds,
        is_completed: completed,
        difficulty
      });

      console.log('Игра сохранена');
    } catch (error) {
      console.error('Ошибка сохранения:', error);
    } finally {
      setSaving(false);
    }
  }, [score, level, lives, difficulty, timePlayed, saving]);

  // Обработка клавиатуры
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'ArrowLeft' || e.key === 'a' || e.key === 'A') {
        keysRef.current.left = true;
      }
      if (e.key === 'ArrowRight' || e.key === 'd' || e.key === 'D') {
        keysRef.current.right = true;
      }
      if (e.key === ' ' || e.key === 'Space') {
        e.preventDefault();
        setPaused(prev => !prev);
      }
    };

    const handleKeyUp = (e) => {
      if (e.key === 'ArrowLeft' || e.key === 'a' || e.key === 'A') {
        keysRef.current.left = false;
      }
      if (e.key === 'ArrowRight' || e.key === 'd' || e.key === 'D') {
        keysRef.current.right = false;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, []);

  // Игровой цикл
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');

    const gameLoop = () => {
      if (paused || gameOver) {
        gameLoopRef.current = requestAnimationFrame(gameLoop);
        return;
      }

      // Очистка
      ctx.fillStyle = '#1a1a2e';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Движение платформы
      if (keysRef.current.left && paddleRef.current.x > 0) {
        paddleRef.current.x -= paddleRef.current.speed;
      }
      if (keysRef.current.right && paddleRef.current.x < canvas.width - paddleRef.current.width) {
        paddleRef.current.x += paddleRef.current.speed;
      }

      // Движение шарика
      ballRef.current.x += ballRef.current.vx;
      ballRef.current.y += ballRef.current.vy;

      // Отскок от стен
      if (ballRef.current.x - ballRef.current.radius <= 0 || 
          ballRef.current.x + ballRef.current.radius >= canvas.width) {
        ballRef.current.vx = -ballRef.current.vx;
      }
      if (ballRef.current.y - ballRef.current.radius <= 0) {
        ballRef.current.vy = -ballRef.current.vy;
      }

      // Отскок от платформы
      const paddle = paddleRef.current;
      const ball = ballRef.current;
      if (ball.y + ball.radius >= canvas.height - 30 &&
          ball.y + ball.radius <= canvas.height - 20 &&
          ball.x >= paddle.x &&
          ball.x <= paddle.x + paddle.width) {
        const hitPos = (ball.x - (paddle.x + paddle.width / 2)) / (paddle.width / 2);
        ball.vx = hitPos * 5;
        ball.vy = -Math.abs(ball.vy);
      }

      // Проверка падения шарика
      if (ball.y - ball.radius > canvas.height) {
        setLives(prev => {
          const newLives = prev - 1;
          if (newLives <= 0) {
            setGameOver(true);
            saveGame(true);
            return 0;
          }
          // Перезапуск шарика
          ball.x = canvas.width / 2;
          ball.y = canvas.height - 50;
          ball.vx = difficulty === 'easy' ? 4 : difficulty === 'hard' ? 6 : 5;
          ball.vy = -(difficulty === 'easy' ? 4 : difficulty === 'hard' ? 6 : 5);
          return newLives;
        });
      }

      // Проверка столкновений с блоками
      blocksRef.current.forEach(block => {
        if (block.destroyed) return;

        if (ball.x + ball.radius > block.x &&
            ball.x - ball.radius < block.x + block.width &&
            ball.y + ball.radius > block.y &&
            ball.y - ball.radius < block.y + block.height) {
          block.destroyed = true;
          ball.vy = -ball.vy;
          setScore(prev => prev + 10);
        }
      });

      // Проверка победы
      const remainingBlocks = blocksRef.current.filter(b => !b.destroyed).length;
      if (remainingBlocks === 0) {
        setLevel(prev => prev + 1);
        initGame();
      }

      // Отрисовка
      // Платформа
      ctx.fillStyle = '#667eea';
      ctx.fillRect(paddle.x, canvas.height - 30, paddle.width, 10);
      ctx.fillStyle = '#764ba2';
      ctx.fillRect(paddle.x, canvas.height - 30, paddle.width, 3);

      // Шарик
      ctx.beginPath();
      ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
      ctx.fillStyle = '#fff';
      ctx.fill();
      ctx.strokeStyle = '#667eea';
      ctx.lineWidth = 2;
      ctx.stroke();

      // Блоки
      blocksRef.current.forEach(block => {
        if (!block.destroyed) {
          ctx.fillStyle = block.color;
          ctx.fillRect(block.x, block.y, block.width, block.height);
          ctx.strokeStyle = '#fff';
          ctx.lineWidth = 2;
          ctx.strokeRect(block.x, block.y, block.width, block.height);
        }
      });

      // Автосохранение каждые 30 секунд
      const currentTime = Math.floor((Date.now() - startTimeRef.current) / 1000);
      if (currentTime > 0 && currentTime % 30 === 0) {
        saveGame(false);
      }

      gameLoopRef.current = requestAnimationFrame(gameLoop);
    };

    gameLoopRef.current = requestAnimationFrame(gameLoop);

    return () => {
      if (gameLoopRef.current) {
        cancelAnimationFrame(gameLoopRef.current);
      }
    };
  }, [paused, gameOver, difficulty, initGame, saveGame]);

  // Инициализация при монтировании
  useEffect(() => {
    loadGame();
  }, [loadGame]);

  const handleNewGame = () => {
    initGame();
  };

  const handleSave = () => {
    saveGame(false);
  };

  return (
    <div className="game-container">
      <div className="game-header">
        <div className="game-stats">
          <div className="stat">
            <span className="stat-label">Счет:</span>
            <span className="stat-value">{score}</span>
          </div>
          <div className="stat">
            <span className="stat-label">Уровень:</span>
            <span className="stat-value">{level}</span>
          </div>
          <div className="stat">
            <span className="stat-label">Жизни:</span>
            <span className="stat-value">{lives}</span>
          </div>
        </div>
        <div className="game-controls">
          <select 
            value={difficulty} 
            onChange={(e) => {
              setDifficulty(e.target.value);
              initGame();
            }}
            className="difficulty-select"
            disabled={!paused && !gameOver}
          >
            <option value="easy">Легкий</option>
            <option value="medium">Средний</option>
            <option value="hard">Сложный</option>
          </select>
          <button onClick={handleSave} className="btn btn-secondary" disabled={saving}>
            {saving ? 'Сохранение...' : 'Сохранить'}
          </button>
          <button onClick={handleNewGame} className="btn btn-primary">
            Новая игра
          </button>
        </div>
      </div>

      <div className="game-canvas-wrapper">
        <canvas ref={canvasRef} className="game-canvas"></canvas>
        {paused && (
          <div className="game-overlay">
            <div className="overlay-content">
              <h2>Пауза</h2>
              <p>Нажмите Пробел для продолжения</p>
            </div>
          </div>
        )}
        {gameOver && (
          <div className="game-overlay">
            <div className="overlay-content">
              <h2>Игра окончена!</h2>
              <p>Ваш счет: {score}</p>
              <p>Уровень: {level}</p>
              <button onClick={handleNewGame} className="btn btn-primary">
                Играть снова
              </button>
            </div>
          </div>
        )}
      </div>

      <div className="game-instructions">
        <p><strong>Управление:</strong> Стрелки влево/вправо или A/D для движения платформы</p>
        <p><strong>Пробел:</strong> Пауза</p>
      </div>
    </div>
  );
};

export default Game;

