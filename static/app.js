const expressionEl = document.getElementById("expression");
const resultEl = document.getElementById("result");

const state = {
  expression: "",
  justEvaluated: false,
};

const displayOps = { "+": "+", "-": "−", "*": "×", "/": "÷" };

function renderExpression() {
  if (!state.expression) {
    expressionEl.textContent = "0";
    return;
  }
  expressionEl.textContent = state.expression.replace(/[+\-*/]/g, (op, index) => {
    const previous = state.expression[index - 1];
    if (op === "-" && (index === 0 || /[+\-*/]/.test(previous))) return "−";
    return displayOps[op];
  });
}

function showResult(text, isError = false) {
  resultEl.textContent = text;
  resultEl.classList.toggle("is-error", isError);
}

function tailParts(expression) {
  let index = expression.length;
  while (index > 0 && /[\d.]/.test(expression[index - 1])) index -= 1;
  const number = expression.slice(index);
  const prefix = expression.slice(0, index);
  const unary =
    prefix.endsWith("-") &&
    (prefix.length === 1 || /[+*/]/.test(prefix.at(-2)));
  return { prefix, number, unary };
}

function clearAll() {
  state.expression = "";
  state.justEvaluated = false;
  renderExpression();
  showResult("0");
}

function appendDigit(digit) {
  if (state.justEvaluated) {
    state.expression = "";
    state.justEvaluated = false;
    showResult("0");
  }
  const { number } = tailParts(state.expression);
  if (number === "0") {
    state.expression = state.expression.slice(0, -1) + digit;
  } else {
    state.expression += digit;
  }
  renderExpression();
}

function appendDecimal() {
  if (state.justEvaluated) {
    state.expression = "0.";
    state.justEvaluated = false;
    showResult("0");
    renderExpression();
    return;
  }
  const { number } = tailParts(state.expression);
  if (number.includes(".")) return;
  if (number === "") state.expression += "0.";
  else state.expression += ".";
  renderExpression();
}

function appendOperator(operator) {
  if (state.justEvaluated) state.justEvaluated = false;
  if (!state.expression) {
    state.expression = operator === "-" ? "-" : "";
    renderExpression();
    return;
  }

  const last = state.expression.at(-1);
  const previous = state.expression.at(-2);
  if (!/[+\-*/]/.test(last)) {
    state.expression += operator;
  } else if (operator === "-" && /[+*/]/.test(last)) {
    state.expression += "-";
  } else if (last === "-" && previous && /[+*/]/.test(previous)) {
    state.expression = operator === "-" ? state.expression : state.expression.slice(0, -2) + operator;
  } else if (state.expression === "-") {
    state.expression = operator === "-" ? "-" : "";
  } else {
    state.expression = state.expression.slice(0, -1) + operator;
  }
  renderExpression();
}

function toggleSign() {
  if (state.justEvaluated) {
    if (resultEl.classList.contains("is-error")) return;
    state.justEvaluated = false;
  }
  const { prefix, number, unary } = tailParts(state.expression);
  if (!number) return;

  if (unary) {
    state.expression = prefix.slice(0, -1) + number;
  } else if (prefix === "") {
    state.expression = `-${number}`;
  } else if (prefix.endsWith("+")) {
    state.expression = `${prefix.slice(0, -1)}-${number}`;
  } else if (prefix.endsWith("-")) {
    state.expression = `${prefix.slice(0, -1)}+${number}`;
  } else {
    state.expression = `${prefix}-${number}`;
  }
  renderExpression();
  if (/^-?\d+(\.\d+)?$/.test(state.expression)) {
    showResult(expressionEl.textContent);
  }
}

function backspace() {
  if (state.justEvaluated) {
    clearAll();
    return;
  }
  state.expression = state.expression.slice(0, -1);
  renderExpression();
  if (!state.expression) showResult("0");
}

async function equals() {
  const expression = state.expression.replace(/[+\-*/.]+$/, "");
  if (!expression) {
    showResult("Error", true);
    return;
  }
  try {
    const response = await fetch("/calculate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ expression }),
    });
    const payload = await response.json();
    if (!response.ok || payload.result === undefined) {
      showResult("Error", true);
      return;
    }
    showResult(payload.result.replace(/^-/, "−"));
    state.expression = payload.result;
    state.justEvaluated = true;
    renderExpression();
  } catch {
    showResult("Error", true);
  }
}

document.querySelector(".keys").addEventListener("click", (event) => {
  const button = event.target.closest("button");
  if (!button) return;
  if (button.dataset.digit) appendDigit(button.dataset.digit);
  else if (button.dataset.op) appendOperator(button.dataset.op);
  else if (button.dataset.action === "decimal") appendDecimal();
  else if (button.dataset.action === "clear") clearAll();
  else if (button.dataset.action === "sign") toggleSign();
  else if (button.dataset.action === "backspace") backspace();
  else if (button.dataset.action === "equals") equals();
});

document.addEventListener("keydown", (event) => {
  if (event.target.closest && event.target.closest("button") && event.key === "Enter") return;
  if (event.key >= "0" && event.key <= "9") appendDigit(event.key);
  else if (event.key === "." || event.key === ",") appendDecimal();
  else if ("+-*/".includes(event.key)) appendOperator(event.key);
  else if (event.key === "Enter" || event.key === "=") {
    event.preventDefault();
    equals();
  } else if (event.key === "Escape") clearAll();
  else if (event.key === "Backspace") {
    event.preventDefault();
    backspace();
  }
});

clearAll();
