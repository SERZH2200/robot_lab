import { api } from "./api.js";
import { renderMaze } from "./maze.js";

const els = {
  connection: document.querySelector("#connectionStatus"),
  mazeTitle: document.querySelector("#mazeTitle"),
  mazeSelect: document.querySelector("#mazeSelect"),
  loadMazeBtn: document.querySelector("#loadMazeBtn"),
  mazeSvg: document.querySelector("#mazeSvg"),
  mazePlaceholder: document.querySelector("#mazePlaceholder"),
  robotPosition: document.querySelector("#robotPosition"),
  lmsDirection: document.querySelector("#lmsDirection"),
  lastAction: document.querySelector("#lastAction"),
  lastResult: document.querySelector("#lastResult"),
  exitDetected: document.querySelector("#exitDetected"),
  completed: document.querySelector("#completed"),
  gameStatusBadge: document.querySelector("#gameStatusBadge"),
  lmsBtn: document.querySelector("#lmsBtn"),
  resetBtn: document.querySelector("#resetBtn"),
  runBtn: document.querySelector("#runBtn"),
  sourceEditor: document.querySelector("#sourceEditor"),
  consoleOutput: document.querySelector("#consoleOutput"),
  clearConsoleBtn: document.querySelector("#clearConsoleBtn"),
  toastContainer: document.querySelector("#toastContainer"),
};

const DEFAULT_PROGRAM = `function work()
begin
    short distance set lms;
    move right;
end
return distance;`;

let snapshot = null;
let actionInProgress = false;
let websocket = null;
let reconnectTimer = null;

function setConnection(status, text) {
  els.connection.classList.remove("online", "offline");
  if (status) els.connection.classList.add(status);
  els.connection.querySelector("span:last-child").textContent = text;
}

function formatAction(action) {
  const names = {
    move_left: "move left",
    move_right: "move right",
    move_vertical: "move",
    lms: "lms",
  };
  return action ? (names[action] || action) : "—";
}

function formatResult(result, action) {
  if (!action) return "—";
  return result === null || result === undefined ? "undefined" : String(result);
}

function yesNo(value) {
  return value ? "да" : "нет";
}

function renderState(nextState) {
    if (!nextState) return;

    const wasCompleted = snapshot?.completed === true;
    snapshot = nextState;
  els.mazePlaceholder.classList.add("hidden");
  els.mazeTitle.textContent = nextState.maze_name || "Лабиринт";
  els.robotPosition.textContent = `(${nextState.robot.position.row}, ${nextState.robot.position.col})`;
  els.lmsDirection.textContent = nextState.robot.lms_direction || "—";
  els.lastAction.textContent = formatAction(nextState.last_action);
  els.lastResult.textContent = formatResult(nextState.last_result, nextState.last_action);
  els.exitDetected.textContent = yesNo(nextState.exit_detected);
  els.completed.textContent = yesNo(nextState.completed);

  els.gameStatusBadge.textContent = nextState.completed ? "Завершён" : "Активен";
  els.gameStatusBadge.classList.toggle("done", Boolean(nextState.completed));
  renderMaze(els.mazeSvg, nextState);

  if (nextState.maze_name && els.mazeSelect.value !== nextState.maze_name) {
    const option = [...els.mazeSelect.options].find(item => item.value === nextState.maze_name);
    if (option) els.mazeSelect.value = nextState.maze_name;
  }
  const movementButtons = document.querySelectorAll("[data-move]");

  movementButtons.forEach(button => {
    button.disabled = nextState.completed;
  });

  els.lmsBtn.disabled = nextState.completed;
  els.runBtn.disabled = nextState.completed;

  if (nextState.completed && !wasCompleted) {
      showConsole(
        "Лабиринт завершён! Робот достиг выхода.",
        "success"
    );

      toast(
        "Лабиринт пройден!",
        "success"
    );
  }
}

function setBusy(busy) {
    actionInProgress = busy;

    const gameCompleted = snapshot?.completed === true;

    document.querySelectorAll("[data-move]").forEach(button => {
        button.disabled = busy || gameCompleted;
    });

    els.lmsBtn.disabled = busy || gameCompleted;

    els.resetBtn.disabled = busy;
    els.loadMazeBtn.disabled = busy;
}

function setRunBusy(busy) {
  els.runBtn.disabled = busy;
  els.runBtn.textContent = busy ? "Выполняется…" : "▶ Запустить";
}

function showConsole(text, type = "") {
  els.consoleOutput.textContent = text;
  els.consoleOutput.classList.remove("error", "success");
  if (type) els.consoleOutput.classList.add(type);
}

function toast(message, type = "") {
  const node = document.createElement("div");
  node.className = `toast ${type}`;
  node.textContent = message;
  els.toastContainer.appendChild(node);
  window.setTimeout(() => node.remove(), 2800);
}

function errorMessage(error) {
  return error instanceof Error ? error.message : String(error);
}

async function executeGameAction(action) {
  if (actionInProgress) return;
  setBusy(true);
  try {
    const response = await action();
    const state = response?.state || response;
    renderState(state);
    return response;
  } catch (error) {
    toast(errorMessage(error), "error");
    throw error;
  } finally {
    setBusy(false);
  }
}

async function loadMazes() {
  const data = await api.mazes();
  els.mazeSelect.replaceChildren();

  for (const name of data.mazes || []) {
    const option = document.createElement("option");
    option.value = name;
    option.textContent = name;
    els.mazeSelect.appendChild(option);
  }

  if (snapshot?.maze_name) els.mazeSelect.value = snapshot.maze_name;
}

async function initialize() {
  els.sourceEditor.value = localStorage.getItem("cellRobotSource") || DEFAULT_PROGRAM;

  try {
    await api.health();
    setConnection("online", "Backend подключён");
    const [state] = await Promise.all([api.state(), loadMazes()]);
    renderState(state);
    connectWebSocket();
  } catch (error) {
    setConnection("offline", "Backend недоступен");
    els.mazePlaceholder.textContent = "Не удалось получить состояние backend.";
    showConsole(errorMessage(error), "error");
  }
}

function connectWebSocket() {
  if (websocket && [WebSocket.OPEN, WebSocket.CONNECTING].includes(websocket.readyState)) return;

  const protocol = location.protocol === "https:" ? "wss:" : "ws:";
  websocket = new WebSocket(`${protocol}//${location.host}/ws/game`);

  websocket.addEventListener("open", () => {
    setConnection("online", "Backend подключён");
    clearInterval(reconnectTimer);
    reconnectTimer = null;
  });

  websocket.addEventListener("message", event => {
    try {
      const message = JSON.parse(event.data);
      if (message.state) renderState(message.state);
      if (message.type === "program_finished") {
        showConsole(`Program finished. work() returned: ${message.result}`, "success");
      }
    } catch (error) {
      console.error("WebSocket message error", error);
    }
  });

  websocket.addEventListener("close", () => {
    setConnection("offline", "Переподключение…");
    if (!reconnectTimer) {
      reconnectTimer = setInterval(connectWebSocket, 1800);
    }
  });

  websocket.addEventListener("error", () => websocket.close());
}

document.querySelectorAll("[data-move]").forEach(button => {
  button.addEventListener("click", async () => {
    const direction = button.dataset.move;
    try {
      const response = await executeGameAction(() => api.move(direction));
      const result = response?.result;
      toast(`${direction}: ${result === null ? "undefined" : result}`);
    } catch {}
  });
});

els.lmsBtn.addEventListener("click", async () => {
  try {
    const response = await executeGameAction(() => api.lms());
    toast(`LMS: ${response.result}`);
  } catch {}
});

els.resetBtn.addEventListener("click", async () => {
  try {
    await executeGameAction(() => api.reset());
    showConsole("Лабиринт сброшен в начальное состояние.");
  } catch {}
});

els.loadMazeBtn.addEventListener("click", async () => {
  const name = els.mazeSelect.value;
  if (!name) return;
  try {
    await executeGameAction(() => api.loadMaze(name));
    showConsole(`Загружен лабиринт: ${name}`);
  } catch {}
});

els.runBtn.addEventListener("click", async () => {
  const source = els.sourceEditor.value.trim();
  if (!source) {
    showConsole("Введите программу.", "error");
    return;
  }

  localStorage.setItem("cellRobotSource", els.sourceEditor.value);
  setRunBusy(true);
  showConsole("Выполнение программы…");

  try {
    const response = await api.run(source);
    renderState(response.state);
    showConsole(`Program finished. work() returned: ${response.result}`, "success");
  } catch (error) {
    showConsole(errorMessage(error), "error");
    toast("Ошибка выполнения программы", "error");
  } finally {
    setRunBusy(false);
  }
});

els.clearConsoleBtn.addEventListener("click", () => showConsole(""));
els.sourceEditor.addEventListener("input", () => localStorage.setItem("cellRobotSource", els.sourceEditor.value));

initialize();
