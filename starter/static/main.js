// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
let puzzle = [];
let solution = [];
let startTime = null;
let timerInterval = null;
let hintsUsed = 0;
const hintColors = ['#FFF59D', '#FFCC80', '#B39DDB', '#A5D6A7', '#FFE082'];

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.inputMode = 'numeric';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      input.dataset.block = Math.floor(i/3)*3 + Math.floor(j/3);
      input.setAttribute('aria-label', `Row ${i+1} Column ${j+1}`);
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz, sol) {
  puzzle = puz;
  solution = sol || [];
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      inp.className = 'sudoku-cell';
      inp.style.background = '';
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.classList.add('prefilled');
      } else {
        inp.value = '';
        inp.disabled = false;
        inp.classList.remove('prefilled');
      }
    }
  }
  resetTimer();
}

function startTimer() {
  startTime = Date.now();
  const el = document.getElementById('timer');
  clearInterval(timerInterval);
  timerInterval = setInterval(() => {
    const diff = Date.now() - startTime;
    el.innerText = formatTime(diff);
  }, 250);
}

function stopTimer() {
  clearInterval(timerInterval);
}

function resetTimer() {
  stopTimer();
  startTime = null;
  document.getElementById('timer').innerText = '00:00';
  hintsUsed = 0;
  document.getElementById('hints-used').innerText = hintsUsed;
}

function formatTime(ms) {
  const s = Math.floor(ms / 1000);
  const mm = String(Math.floor(s / 60)).padStart(2, '0');
  const ss = String(s % 60).padStart(2, '0');
  return `${mm}:${ss}`;
}

async function newGame() {
  const difficulty = document.getElementById('difficulty').value;
  const res = await fetch(`/new?difficulty=${encodeURIComponent(difficulty)}`);
  const data = await res.json();
  renderPuzzle(data.puzzle, data.solution);
  document.getElementById('message').innerText = '';
  startTimer();
  loadTopTimes();
}

function getBoardValues() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  return board;
}

async function checkSolution() {
  const board = getBoardValues();
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.className = 'error';
    msg.innerText = data.error;
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0]*SIZE + x[1]));
  const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    inp.classList.remove('incorrect');
    if (incorrect.has(idx)) {
      inp.classList.add('incorrect');
    }
  }
  if (incorrect.size === 0) {
    msg.className = 'success';
    msg.innerText = `Correct! Time: ${document.getElementById('timer').innerText} - Hints: ${hintsUsed}`;
    stopTimer();
    // Save to top times
    setTimeout(() => {
      const name = prompt('You made the Top list! Enter your name:', 'Player');
      saveTopTime({name: name || 'Player', time: Date.now() - startTime, hints: hintsUsed, difficulty: document.getElementById('difficulty').value});
      loadTopTimes();
    }, 200);
  } else {
    msg.className = 'error';
    msg.innerText = 'Some cells are incorrect.';
  }
}

function pickHintCell() {
  const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  const candidates = [];
  for (let i = 0; i < inputs.length; i++) {
    const inp = inputs[i];
    if (inp.disabled) continue;
    if (!inp.value) candidates.push({idx: i, inp});
  }
  if (candidates.length === 0) return null;
  return candidates[Math.floor(Math.random() * candidates.length)];
}

function useHint() {
  if (!solution || solution.length === 0) return;
  const sel = pickHintCell();
  if (!sel) {
    document.getElementById('message').innerText = 'No empty cells to hint.';
    return;
  }
  const idx = sel.idx;
  const i = Math.floor(idx / SIZE);
  const j = idx % SIZE;
  const val = solution[i][j];
  const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  const inp = inputs[idx];
  inp.value = val;
  inp.disabled = true;
  inp.classList.add('hint');
  const color = hintColors[hintsUsed % hintColors.length];
  inp.style.background = color;
  hintsUsed += 1;
  document.getElementById('hints-used').innerText = hintsUsed;
}

function validateImmediate(e) {
  const target = e.target;
  if (!target || !target.dataset) return;
  if (!target.matches('.sudoku-cell') || target.disabled) return;
  let val = target.value.replace(/[^1-9]/g, '');
  target.value = val;
  // Highlight duplicates in row/col/block
  const r = parseInt(target.dataset.row, 10);
  const c = parseInt(target.dataset.col, 10);
  const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  // clear previous invalids for this row/col/block
  for (let k = 0; k < inputs.length; k++) {
    inputs[k].classList.remove('invalid');
  }
  if (!val) return;
  const n = parseInt(val, 10);
  // scan for duplicates
  for (let i = 0; i < SIZE; i++) {
    const idxRow = r * SIZE + i;
    const idxCol = i * SIZE + c;
    if (inputs[idxRow] && idxRow !== (r*SIZE + c) && inputs[idxRow].value == val) {
      inputs[idxRow].classList.add('invalid');
      target.classList.add('invalid');
    }
    if (inputs[idxCol] && idxCol !== (r*SIZE + c) && inputs[idxCol].value == val) {
      inputs[idxCol].classList.add('invalid');
      target.classList.add('invalid');
    }
  }
  // block check
  const blockRow = Math.floor(r/3)*3;
  const blockCol = Math.floor(c/3)*3;
  for (let i = 0; i < 3; i++) {
    for (let j = 0; j < 3; j++) {
      const idx = (blockRow + i) * SIZE + (blockCol + j);
      if (idx === (r*SIZE + c)) continue;
      if (inputs[idx].value == val) {
        inputs[idx].classList.add('invalid');
        target.classList.add('invalid');
      }
    }
  }
}

function loadTopTimes() {
  const raw = localStorage.getItem('sudoku_top_times') || '[]';
  let arr = [];
  try { arr = JSON.parse(raw); } catch(e) { arr = []; }
  arr.sort((a,b) => a.time - b.time);
  arr = arr.slice(0,10);
  const ol = document.getElementById('top-times-list');
  ol.innerHTML = '';
  arr.forEach(item => {
    const li = document.createElement('li');
    li.textContent = `${item.name} — ${formatTime(item.time)} — Hints: ${item.hints} — ${item.difficulty}`;
    ol.appendChild(li);
  });
}

function saveTopTime(entry) {
  const raw = localStorage.getItem('sudoku_top_times') || '[]';
  let arr = [];
  try { arr = JSON.parse(raw); } catch(e) { arr = []; }
  arr.push(entry);
  arr.sort((a,b) => a.time - b.time);
  arr = arr.slice(0,10);
  localStorage.setItem('sudoku_top_times', JSON.stringify(arr));
}

function toggleTheme() {
  const body = document.body;
  const btn = document.getElementById('theme-toggle');
  if (body.dataset.theme === 'dark') {
    body.dataset.theme = 'light';
    btn.setAttribute('aria-pressed','false');
  } else {
    body.dataset.theme = 'dark';
    btn.setAttribute('aria-pressed','true');
  }
}

window.addEventListener('load', () => {
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('hint-btn').addEventListener('click', useHint);
  document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
  // event delegation for inputs
  document.getElementById('sudoku-board').addEventListener('input', validateImmediate);
  // initialize
  newGame();
  loadTopTimes();
});