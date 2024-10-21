import { useEffect, useRef, useState } from "react";
import { fabric } from "fabric";
import { ICheckerPositions, IGameData } from "../types/backgammon.types";

const POINTS = 24;

const LIGHT_BAR_COLOR = "#F5D6B5";
const DARK_BAR_COLOR = "#8B5A2B";
const PLAYER_1_COLOR = "#FFF";
const PLAYER_2_COLOR = "#F00";
const BAR_COLOR = "#333333";
const DEFAULT_WIDTH = 900;

const calculateAspectRatio = (width: number) =>
  width / (width - (width / 13) * 3);

const getX = (index: number, width: number, barWidth: number) => {
  if (index <= 6) {
    // Bottom right (points 1-6)
    return width - index * barWidth;
  } else if (index <= 12) {
    // Bottom left (points 7-12)
    return width - (index + 1) * barWidth;
  } else if (index <= 18) {
    // Top left (points 13-18)
    return (index - 13) * barWidth;
  } else {
    // Top left (points 19-24)
    return (index - 12) * barWidth;
  }
};

const BackgammonBoard = ({
  gameData,
  onMoveChecker = () => {},
  readOnly = false,
}: {
  gameData: IGameData;
  onMoveChecker?: (updatedCheckerPositions: ICheckerPositions) => void;
  readOnly?: boolean;
}) => {
  const { checkerPositions } = gameData;

  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const fabricRef = useRef<fabric.Canvas | null>(null);

  const [boardSize, setBoardSize] = useState<{ width: number; height: number }>(
    {
      width: DEFAULT_WIDTH,
      height: DEFAULT_WIDTH / calculateAspectRatio(DEFAULT_WIDTH),
    }
  );

  const renderBoard = () => {
    const canvas = fabricRef.current;

    if (!canvas) return;

    const { width, height } = boardSize;
    const barWidth = width / 13;
    const barHeight = height / 2 - height / 25 / calculateAspectRatio(width);

    canvas.clear();

    const bar = new fabric.Rect({
      left: width / 2 - barWidth / 2,
      top: 0,
      width: barWidth,
      height: height,
      fill: BAR_COLOR,
      selectable: false,
    });
    canvas.add(bar);

    for (let i = 1; i <= POINTS; i++) {
      const isTopHalf = i > 12;
      const x = getX(i, width, barWidth);
      const y = isTopHalf ? barHeight : height;
      const angle = isTopHalf ? 180 : 0;

      const fillColor = i % 2 === 0 ? LIGHT_BAR_COLOR : DARK_BAR_COLOR;

      const triangle = new fabric.Triangle({
        left: x + barWidth / 2,
        top: isTopHalf ? y : y - barHeight,
        width: barWidth,
        height: barHeight,
        fill: fillColor,
        angle: angle,
        selectable: false,
        originX: "center",
      });

      canvas.add(triangle);
    }
  };

  const renderCheckers = () => {
    const canvas = fabricRef.current;

    if (!canvas) return;

    const { width, height } = boardSize;
    const barWidth = width / 13;
    const checkerRadius = barWidth / 2;

    for (let boardIndex = 1; boardIndex <= POINTS; boardIndex++) {
      const checkers = checkerPositions[boardIndex];
      const isTopHalf = boardIndex > 12;
      const x = getX(boardIndex, width, barWidth);
      const y = isTopHalf ? 0 : height;

      checkers.forEach((player, index) => {
        const checkerY = isTopHalf
          ? y + checkerRadius + index * 2 * checkerRadius
          : y - (checkerRadius + index * 2 * checkerRadius);

        const aspectRatio = calculateAspectRatio(width);
        const checker = new fabric.Circle({
          left: x + barWidth / 2,
          top: checkerY - checkerRadius,
          radius: checkerRadius - 1 / aspectRatio,
          fill: player === "player_1" ? PLAYER_1_COLOR : PLAYER_2_COLOR,
          hasControls: false,
          hasBorders: false,
          lockRotation: true,
          originX: "center",
          stroke: "#000",
          strokeWidth: 1 / aspectRatio,
          selectable: !readOnly, // Disable movement if readOnly is true
          data: player,
        });

        if (!readOnly) {
          checker.on("moving", () =>
            snapToGrid(checker, barWidth, checkerRadius)
          );
          checker.on("modified", () =>
            updateCheckerPosition(checker, boardIndex, index, barWidth)
          );
        }

        canvas.add(checker);
      });
    }
  };

  const snapToGrid = (
    checker: fabric.Circle,
    barWidth: number,
    checkerRadius: number
  ) => {
    const { left, top } = checker;
    const { width } = boardSize;

    let snappedLeft = Math.round(left! / barWidth) * barWidth + checkerRadius;

    if (snappedLeft > width) {
      snappedLeft = width - barWidth + checkerRadius;
    } else if (snappedLeft < 0) {
      snappedLeft = checkerRadius;
    }

    const snappedTop =
      Math.round(top! / (2 * checkerRadius)) * (2 * checkerRadius);

    checker.set({
      left: snappedLeft,
      top: snappedTop,
    });

    checker.setCoords();
  };

  const updateCheckerPosition = (
    checker: fabric.Circle,
    originalPointIndex: number,
    checkerIndex: number,
    barWidth: number
  ) => {
    let newPointIndex: number;

    const column = Math.floor(checker.left! / barWidth);

    if (column === 6) {
      newPointIndex = -1;
    } else if (checker.top! > boardSize.height / 2) {
      // Bottom half (points 1 to 12)
      newPointIndex = column < 6 ? 12 - column : 13 - column;
    } else {
      // Top half (points 13 to 24)
      newPointIndex = column < 6 ? column + 13 : column + 12;
    }

    const updatedPositions = JSON.parse(JSON.stringify(checkerPositions));

    const checkerToMove = updatedPositions[originalPointIndex][checkerIndex];

    updatedPositions[originalPointIndex].splice(checkerIndex, 1);

    if (newPointIndex > 0) {
      if (!updatedPositions[newPointIndex]) {
        updatedPositions[newPointIndex] = [];
      }
      updatedPositions[newPointIndex].push(checkerToMove);
    }

    onMoveChecker(updatedPositions);
  };

  useEffect(() => {
    if (!canvasRef.current) return;

    const canvasElement = new fabric.Canvas(canvasRef.current, {
      width: boardSize.width,
      height: boardSize.height,
      selection: false,
    });

    fabricRef.current = canvasElement;

    renderBoard();
    renderCheckers();

    return () => {
      canvasElement.dispose();
    };
  }, [checkerPositions, boardSize]);

  useEffect(() => {
    if (!canvasRef.current) return;

    const handleResize = () => {
      const parent = canvasRef.current?.parentElement;

      const containerWidth =
        parent?.parentElement?.clientWidth || window.innerWidth * 0.5;
      const newWidth = containerWidth;
      const newHeight = containerWidth / calculateAspectRatio(newWidth);

      setBoardSize({ width: newWidth, height: newHeight });
    };

    window.addEventListener("resize", handleResize);

    handleResize();

    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, [canvasRef.current]);

  return (
    <div className="relative w-full h-full">
      <div className="absolute inset-0">
        <canvas ref={canvasRef} />
      </div>
    </div>
  );
};

export default BackgammonBoard;
