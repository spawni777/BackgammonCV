import { createApi } from "@reduxjs/toolkit/query/react";
import { fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import { IGameData } from "../types/backgammon.types";

const BASE_URL = import.meta.env.VITE_API_URL + "/api/backgammon/";

export const backgammonApi = createApi({
  reducerPath: "uploader",
  baseQuery: fetchBaseQuery({
    baseUrl: BASE_URL,
  }),
  endpoints: (builder) => ({
    detectBoard: builder.mutation({
      query: ({ body, signal }: { body: FormData; signal?: AbortSignal }) => ({
        url: "/detect",
        method: "POST",
        body,
        signal,
        responseHandler: (response: any) => {
          if (!response.ok) {
            throw new Error(response.statusText);
          }
          return response.blob();
        },
      }),
      transformResponse: async (response: Blob | void) => {
        if (response instanceof Blob) {
          const file = new File([response], "board.jpg");
          const url = window.URL.createObjectURL(file);
          return url;
        }
      },
    }),
    parseBoard: builder.mutation({
      query: ({ body, signal }: { body: FormData; signal?: AbortSignal }) => ({
        url: "/parse",
        method: "POST",
        body,
        signal,
      }),
    }),
    getHints: builder.mutation({
      query: ({ body, signal }: { body: IGameData; signal?: AbortSignal }) => ({
        url: "/hint",
        method: "POST",
        body,
        signal,
      }),
    }),
    deleteGameData: builder.query<{body: {success: boolean;}}, void>({
      query: () => ({
        url: "/game-data",
        method: "DELETE",
      }),
    }),
  }),
});

// auto-generated based on the defined endpoints
export const {
  useDetectBoardMutation,
  useParseBoardMutation,
  useGetHintsMutation,
  useDeleteGameDataQuery,
} = backgammonApi;
