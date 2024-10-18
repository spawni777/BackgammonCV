import { configureStore, ThunkAction, Action } from "@reduxjs/toolkit";

import { backgammonApi } from "../api/backgammon.api";
import backgammonReducer, {
  backgammonSlice,
} from "../reducers/backgammon.slice";

const reducer = {
  [backgammonSlice.name]: backgammonReducer,
  [backgammonApi.reducerPath]: backgammonApi.reducer,
};

export const store = configureStore({
  reducer,
  devTools: process.env.NODE_ENV !== "production",
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(backgammonApi.middleware),
});

export type AppDispatch = typeof store.dispatch;
export type RootState = ReturnType<typeof store.getState>;
export type AppThunk<ReturnType = void> = ThunkAction<
  ReturnType,
  RootState,
  unknown,
  Action<string>
>;
