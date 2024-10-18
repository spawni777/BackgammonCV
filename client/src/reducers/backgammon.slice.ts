import { createSlice } from "@reduxjs/toolkit";
import { RootState } from "@/app/store";
import { IGameData } from "../types/backgammon.types";

interface BackgammonState {
  gameData: IGameData;
  hints: string[];
}

export const generateEmptyCheckerPositions = () => {
  const checkerPositions: { [key: string]: string[] } = {};

  for (let i = 1; i <= 24; i++) {
    checkerPositions[i.toString()] = [];
  }

  return checkerPositions;
};

const initialBoard: IGameData = {
  checker_positions: generateEmptyCheckerPositions(),
  dices: [],
};
const initialState: BackgammonState = {
  gameData: initialBoard,
  hints: [],
};

export const backgammonSlice = createSlice({
  name: "backgammon",
  initialState,
  reducers: {
    setGameData: (state, action) => {
      state.gameData = action.payload;
    },
    setHints: (state, action) => {
      state.hints = action.payload;
    },
  },
});

export const { setGameData, setHints } = backgammonSlice.actions;

export const selectGameData = (state: RootState): IGameData =>
  state.backgammon.gameData;

export const selectHints = (state: RootState): string[] =>
  state.backgammon.hints;

export default backgammonSlice.reducer;
