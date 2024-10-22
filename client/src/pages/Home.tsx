import BackgammonBoard from "../components/BackgammonBoard";
import useBackgammonSocket from "../hooks/useBackgammonSocket";

const Home = () => {
  const { gameData } = useBackgammonSocket();

  return (
    <div>
      {gameData && (
        <div className="flex flex-col items-center h-screen">
          <h1 className="text-[40px] mb-2">Client Side</h1>
          <h2 className="mb-2">Current player turn: {gameData.currentPlayer}</h2>
          <div className="flex w-2/4">
            <BackgammonBoard readOnly={true} gameData={gameData} showDices={true} />
          </div>
        </div> 
      )}
      {!gameData && (
        <div>
          <div>Loading...</div>
        </div>
      )}
    </div> 
  )
}

export default Home;