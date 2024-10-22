export interface ICheckerPositions {
  [boardIndex: string]: string[];
}

export interface IGameData {
  checkerPositions: ICheckerPositions;
  dices: {
    value: number;
    randomized: boolean;
  }[];
  currentPlayer?: string;
}
