const SVG_NS = "http://www.w3.org/2000/svg";
const TRIANGLE_WIDTH = 72;
const TRIANGLE_HEIGHT = 62;
const HORIZONTAL_STEP = TRIANGLE_WIDTH / 2;
const PADDING = 28;

function svgElement(tag, attrs = {}) {
  const node = document.createElementNS(SVG_NS, tag);
  for (const [name, value] of Object.entries(attrs)) {
    node.setAttribute(name, String(value));
  }
  return node;
}

function triangleGeometry(row, col, orientation) {
  const x = PADDING + col * HORIZONTAL_STEP;
  const y = PADDING + row * TRIANGLE_HEIGHT;

  if (orientation === "up") {
    const left = [x, y + TRIANGLE_HEIGHT];
    const top = [x + TRIANGLE_WIDTH / 2, y];
    const right = [x + TRIANGLE_WIDTH, y + TRIANGLE_HEIGHT];
    return {
      points: [left, top, right],
      sides: {
        left: [left, top],
        right: [top, right],
        vertical: [left, right],
      },
    };
  }

  const left = [x, y];
  const bottom = [x + TRIANGLE_WIDTH / 2, y + TRIANGLE_HEIGHT];
  const right = [x + TRIANGLE_WIDTH, y];
  return {
    points: [left, bottom, right],
    sides: {
      left: [left, bottom],
      right: [bottom, right],
      vertical: [left, right],
    },
  };
}

function pointsAttribute(points) {
  return points.map(([x, y]) => `${x},${y}`).join(" ");
}

function centroid(points) {
  const sum = points.reduce((acc, [x, y]) => [acc[0] + x, acc[1] + y], [0, 0]);
  return [sum[0] / points.length, sum[1] / points.length];
}

function drawLine(svg, endpoints, cssClass) {
  const [[x1, y1], [x2, y2]] = endpoints;
  svg.appendChild(svgElement("line", { x1, y1, x2, y2, class: cssClass }));
}

function cellKey(row, col) {
  return `${row}:${col}`;
}

export function renderMaze(svg, snapshot) {
  const maze = snapshot?.maze;
  if (!maze) {
    svg.replaceChildren();
    return;
  }

  const width = PADDING * 2 + Math.max(0, maze.cols - 1) * HORIZONTAL_STEP + TRIANGLE_WIDTH;
  const height = PADDING * 2 + maze.rows * TRIANGLE_HEIGHT;
  svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
  svg.setAttribute("width", width);
  svg.setAttribute("height", height);

  const fragment = document.createDocumentFragment();
  const geometryByCell = new Map();

  for (const cell of maze.cells) {
    const geometry = triangleGeometry(cell.row, cell.col, cell.orientation);
    geometryByCell.set(cellKey(cell.row, cell.col), geometry);

    fragment.appendChild(svgElement("polygon", {
      points: pointsAttribute(geometry.points),
      class: `triangle-cell ${cell.orientation === "down" ? "alt" : ""}`,
    }));
  }

  for (const cell of maze.cells) {
    const geometry = geometryByCell.get(cellKey(cell.row, cell.col));
    for (const side of cell.walls || []) {
      if (geometry.sides[side]) {
        drawLine(fragment, geometry.sides[side], "maze-wall");
      }
    }
  }

  const exitGeometry = geometryByCell.get(cellKey(maze.exit.row, maze.exit.col));
  if (exitGeometry?.sides?.[maze.exit.side]) {
    drawLine(fragment, exitGeometry.sides[maze.exit.side], "maze-exit");

    const [[x1, y1], [x2, y2]] = exitGeometry.sides[maze.exit.side];
    const label = svgElement("text", {
      x: (x1 + x2) / 2,
      y: (y1 + y2) / 2 - 7,
      "text-anchor": "middle",
      class: "exit-label",
    });
    label.textContent = "EXIT";
    fragment.appendChild(label);
  }

  const robotPosition = snapshot.robot?.position;
  const robotGeometry = robotPosition
    ? geometryByCell.get(cellKey(robotPosition.row, robotPosition.col))
    : null;

  if (robotGeometry) {
    const [cx, cy] = centroid(robotGeometry.points);
    fragment.appendChild(svgElement("circle", { cx, cy, r: 14, class: "robot-body" }));
    fragment.appendChild(svgElement("circle", { cx, cy, r: 4.5, class: "robot-core" }));
  }

  svg.replaceChildren(fragment);
}
