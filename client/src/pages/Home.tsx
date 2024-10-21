import BackgammonBoard from "../components/BackgammonBoard";
import useBackgammonSocket from "../hooks/useBackgammonSocket";

const Home = () => {
  const { gameData } = useBackgammonSocket();

  return (
    <div>
      {gameData && (
        <BackgammonBoard readOnly={true} gameData={gameData} />
      )}
      {!gameData && (
        <div>NO GAME SESSION FOUND</div>
      )}
    </div> 
  )
}

export default Home;