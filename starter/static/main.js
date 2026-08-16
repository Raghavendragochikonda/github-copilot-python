// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
const LEADERBOARD_KEY = 'sudoku-top-10-leaderboard';
const THEME_KEY = 'sudoku-theme';
let puzzle = [];

// Timer state
let timerInterval = null;
let elapsedSeconds = 0;
let timerRunning = false;
let hintsUsed = 0;

function applyTheme(theme) {
  const resolvedTheme = theme === 'dark' ? 'dark' : 'light';
  document.body.dataset.theme = resolvedTheme;
  const toggleButton = document.getElementById('theme-toggle');
  if (toggleButton) {
    toggleButton.textContent = resolvedTheme === 'dark' ? 'Light Mode' : 'Dark Mode';
  }
  localStorage.setItem(THEME_KEY, resolvedTheme);
}

function initTheme() {
  const savedTheme = localStorage.getItem(THEME_KEY);
  const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  const initialTheme = savedTheme || (prefersDark ? 'dark' : 'light');
  applyTheme(initialTheme);
}

function getLeaderboardEntries() {
  try {
    const raw = localStorage.getItem(LEADERBOARD_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (error) {
    return [];
  }
}

function saveLeaderboardEntries(entries) {
  localStorage.setItem(LEADERBOARD_KEY, JSON.stringify(entries.slice(0, 10)));
}

function formatLeaderboardTime(seconds) {
  return formatTime(seconds);
}

function renderLeaderboard() {
  const list = document.getElementById('leaderboard-list');
  const entries = getLeaderboardEntries()
    .slice()
    .sort((a, b) => {
      const aTime = Number(a.completionTimeSeconds ?? 0);
      const bTime = Number(b.completionTimeSeconds ?? 0);
      if (aTime !== bTime) return aTime - bTime;
      return Number(a.hintsUsed ?? 0) - Number(b.hintsUsed ?? 0);
    })
    .slice(0, 10);

  list.innerHTML = '';

  if (entries.length === 0) {
    const emptyItem = document.createElement('li');
    emptyItem.className = 'empty-leaderboard';
    emptyItem.textContent = 'No completed games yet.';
    list.appendChild(emptyItem);
    return;
  }

  entries.forEach((entry) => {
    const item = document.createElement('li');
    const meta = document.createElement('span');
    meta.className = 'leaderboard-meta';
    meta.textContent = `${entry.playerName} — ${entry.difficulty} — ${formatLeaderboardTime(entry.completionTimeSeconds)} — Hints: ${entry.hintsUsed}`;
    item.appendChild(meta);
    list.appendChild(item);
  });
}

function clearLeaderboard() {
  const confirmed = window.confirm('Clear the Top 10 leaderboard?');
  if (!confirmed) {
    return;
  }
  localStorage.removeItem(LEADERBOARD_KEY);
  renderLeaderboard();
}

function saveCompletedGame() {
  const playerName = window.prompt('You solved it! Enter your name for the leaderboard:', 'Player') || 'Player';
  const cleanName = String(playerName).trim() || 'Player';
  const entries = getLeaderboardEntries();
  entries.push({
    playerName: cleanName,
    completionTimeSeconds: elapsedSeconds,
    difficulty: document.getElementById('difficulty').value,
    hintsUsed: hintsUsed
  });

  entries.sort((a, b) => {
    if (a.completionTimeSeconds !== b.completionTimeSeconds) {
      return a.completionTimeSeconds - b.completionTimeSeconds;
    }
    return a.hintsUsed - b.hintsUsed;
  });

  saveLeaderboardEntries(entries);
  renderLeaderboard();
}

function updateLiveValidation() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  const protectedCells = new Set();

  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const inp = inputs[idx];
      const val = inp.value.trim();
      board[i][j] = val ? parseInt(val, 10) : 0;
      if (inp.disabled) {
        protectedCells.add(`${i},${j}`);
      }
    }
  }

  const conflictSet = new Set();

  for (let row = 0; row < SIZE; row++) {
    const seen = new Map();
    for (let col = 0; col < SIZE; col++) {
      const value = board[row][col];
      if (value === 0 || protectedCells.has(`${row},${col}`)) continue;
      if (seen.has(value)) {
        conflictSet.add(`${row},${seen.get(value)}`);
        conflictSet.add(`${row},${col}`);
      } else {
        seen.set(value, col);
      }
    }
  }

  for (let col = 0; col < SIZE; col++) {
    const seen = new Map();
    for (let row = 0; row < SIZE; row++) {
      const value = board[row][col];
      if (value === 0 || protectedCells.has(`${row},${col}`)) continue;
      if (seen.has(value)) {
        conflictSet.add(`${seen.get(value)},${col}`);
        conflictSet.add(`${row},${col}`);
      } else {
        seen.set(value, row);
      }
    }
  }

  for (let startRow = 0; startRow < SIZE; startRow += 3) {
    for (let startCol = 0; startCol < SIZE; startCol += 3) {
      const seen = new Map();
      for (let row = startRow; row < startRow + 3; row++) {
        for (let col = startCol; col < startCol + 3; col++) {
          const value = board[row][col];
          if (value === 0 || protectedCells.has(`${row},${col}`)) continue;
          if (seen.has(value)) {
            const [firstRow, firstCol] = seen.get(value);
            conflictSet.add(`${firstRow},${firstCol}`);
            conflictSet.add(`${row},${col}`);
          } else {
            seen.set(value, [row, col]);
          }
        }
      }
    }
  }

  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    const row = Number(inp.dataset.row);
    const col = Number(inp.dataset.col);
    const isProtected = inp.disabled || protectedCells.has(`${row},${col}`);
    const isConflict = conflictSet.has(`${row},${col}`);

    inp.classList.remove('conflict', 'incorrect', 'hinted', 'prefilled');

    if (isProtected) {
      if (inp.dataset.hinted === 'true') {
        inp.classList.add('hinted');
      } else if (inp.disabled && inp.value !== '') {
        inp.classList.add('prefilled');
      }
      continue;
    }

    if (isConflict) {
      inp.classList.add('conflict');
    }
  }
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      input.addEventListener('input', (e) => {
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
        updateLiveValidation();
      });
      input.addEventListener('blur', () => {
        updateLiveValidation();
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        delete inp.dataset.hinted;
        inp.className = 'sudoku-cell prefilled';
      } else {
        inp.value = '';
        inp.disabled = false;
        delete inp.dataset.hinted;
        inp.className = 'sudoku-cell';
      }
    }
  }
  updateLiveValidation();
}

function getBoardFromInputs() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value.trim();
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  return board;
}

function getEmptyCellFromBoard(board) {
  for (let row = 0; row < SIZE; row++) {
    for (let col = 0; col < SIZE; col++) {
      if (board[row][col] === 0) {
        return { row, col };
      }
    }
  }
  return null;
}

// Timer utility functions
function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}

function updateTimerDisplay() {
  const timerElement = document.getElementById('timer');
  timerElement.textContent = formatTime(elapsedSeconds);
}

function startTimer() {
  if (timerRunning) return; // Already running
  
  timerRunning = true;
  timerInterval = setInterval(() => {
    elapsedSeconds++;
    updateTimerDisplay();
  }, 1000);
}

function stopTimer() {
  if (!timerRunning) return; // Not running
  
  timerRunning = false;
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
}

function resetTimer() {
  stopTimer();
  elapsedSeconds = 0;
  updateTimerDisplay();
}

async function newGame() {
  const difficulty = document.getElementById('difficulty').value;
  const url = `/new?difficulty=${difficulty}`;
  const res = await fetch(url);
  const data = await res.json();
  renderPuzzle(data.puzzle);
  document.getElementById('message').innerText = '';
  hintsUsed = 0;
  
  // Reset and start the timer
  resetTimer();
  startTimer();
}

async function checkSolution() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  const protectedCells = [];

  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const inp = inputs[idx];
      const val = inp.value.trim();
      board[i][j] = val ? parseInt(val, 10) : 0;
      if (inp.disabled) {
        protectedCells.push([i, j]);
      }
    }
  }

  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board, protected: protectedCells})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }

  const incorrect = new Set(data.incorrect.map(x => x[0] * SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) {
      inp.className = inp.dataset.hinted === 'true' ? 'sudoku-cell hinted' : 'sudoku-cell prefilled';
      continue;
    }
    inp.className = 'sudoku-cell';
    if (incorrect.has(idx)) {
      inp.className = 'sudoku-cell incorrect';
    }
  }

  if (incorrect.size === 0) {
    stopTimer();
    msg.style.color = '#388e3c';
    msg.innerText = 'Congratulations! You solved it!';
    saveCompletedGame();
  } else {
    msg.style.color = '#d32f2f';
    msg.innerText = 'Some cells are incorrect.';
  }
}

async function getHint() {
  const board = getBoardFromInputs();
  const hintCell = getEmptyCellFromBoard(board);
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const msg = document.getElementById('message');

  if (!hintCell) {
    msg.style.color = '#d32f2f';
    msg.innerText = 'No empty cells left to hint.';
    return;
  }

  const idx = hintCell.row * SIZE + hintCell.col;
  const inp = inputs[idx];
  if (!inp || inp.disabled || inp.value !== '') {
    msg.style.color = '#d32f2f';
    msg.innerText = 'Hint target must be an empty cell.';
    return;
  }

  const res = await fetch('/hint', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      board,
      row: hintCell.row,
      col: hintCell.col
    })
  });
  const data = await res.json();

  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }

  if (inp.value !== '' || inp.disabled) {
    msg.style.color = '#d32f2f';
    msg.innerText = 'That cell already contains user input.';
    return;
  }

  hintsUsed += 1;
  inp.value = data.value;
  inp.disabled = true;
  inp.dataset.hinted = 'true';
  inp.className = 'sudoku-cell hinted';
  msg.style.color = '#1976d2';
  msg.innerText = 'Hint used: a correct value has been revealed.';
}

// Wire buttons
window.addEventListener('load', () => {
  initTheme();
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('hint').addEventListener('click', getHint);
  document.getElementById('clear-leaderboard').addEventListener('click', clearLeaderboard);
  document.getElementById('theme-toggle').addEventListener('click', () => {
    const nextTheme = document.body.dataset.theme === 'dark' ? 'light' : 'dark';
    applyTheme(nextTheme);
  });
  renderLeaderboard();
  // initialize
  newGame();
});