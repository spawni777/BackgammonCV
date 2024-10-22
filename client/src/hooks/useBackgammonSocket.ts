import { useEffect, useState } from "react";
import { io, Socket } from "socket.io-client";
import { IGameData } from "../types/backgammon.types";

const useBackgammonSocket = () => {
  const [gameData, setGameData] = useState<IGameData | null>(null);
  const [socket, setSocket] = useState<Socket | null>(null);

  useEffect(() => {
    const newSocket = io(import.meta.env.VITE_API_URL, {
      transports: ['websocket'],
    });
    setSocket(newSocket);

    newSocket.on('game_data', (newGameData: IGameData) => {
      console.log(newGameData);
      setGameData(newGameData);
    });

    return () => {
      newSocket.close();
    };
  }, []);

  return { gameData, socket };
};

export default useBackgammonSocket;
