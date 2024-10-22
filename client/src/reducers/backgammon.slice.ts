import { createSlice } from "@reduxjs/toolkit";
import { RootState } from "@/app/store";
import { IGameData } from "../types/backgammon.types";
import { generateStartPosition } from "@/utils";

interface BackgammonState {
  gameData: IGameData;
  hints: string[];
}

const initialState: BackgammonState = {
  gameData: {
    checkerPositions: generateStartPosition(),
    dices: [],
    currentPlayer: undefined,
  },
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
