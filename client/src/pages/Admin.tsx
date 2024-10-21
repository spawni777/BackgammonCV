import { useEffect, useRef, useState } from "react";
import WebcamCapture from "../components/WebcamCapture";
import {
  useDetectBoardMutation,
  useGetHintsMutation,
  useParseBoardMutation,
} from "../api/backgammon.api";
import { useAppDispatch, useAppSelector } from "../app/hooks";
import {
  selectGameData,
  selectHints,
  setGameData,
  setHints,
} from "../reducers/backgammon.slice";
import BackgammonBoard from "../components/BackgammonBoard";
import { ICheckerPositions } from "../types/backgammon.types";

const Admin = () => {
  const dispatch = useAppDispatch();

  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const hints = useAppSelector(selectHints);
  const gameData = useAppSelector(selectGameData);

  const [detectBoard] = useDetectBoardMutation();
  const [parseBoard] = useParseBoardMutation();
  const [getHints] = useGetHintsMutation();

  const detectionAbortControllerRef = useRef<AbortController | null>(null);
  const parseAbortControllerRef = useRef<AbortController | null>(null);
  const hintAbortControllerRef = useRef<AbortController | null>(null);

  const handleDetection = async (file: File) => {
    if (detectionAbortControllerRef.current) {
      detectionAbortControllerRef.current.abort();
    }

    const abortController = new AbortController();
    detectionAbortControllerRef.current = abortController;

    const formData = new FormData();
    formData.append("image", file);

    dispatch(setHints([]));
    setErrorMessage("");
    setLoading(true);

    try {
      const imageUrl = await detectBoard({
        body: formData,
        signal: abortController.signal,
      }).unwrap();

      if (!imageUrl) {
        throw new Error("Failed to detect board.");
      }

      setImageUrl(imageUrl);

      const gameData = await parseBoard({
        body: formData,
        signal: abortController.signal,
      }).unwrap();

      dispatch(setGameData(gameData));

      await handleGetHint();
    } catch (error) {
      const errorMessage = JSON.stringify(error);
      console.error("Error during detection, parsing or getting hints:", error);
      setErrorMessage(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleGetHint = async () => {
    if (hintAbortControllerRef.current) {
      hintAbortControllerRef.current.abort();
    }

    const abortController = new AbortController();
    hintAbortControllerRef.current = abortController;

    const hints = await getHints({
      body: gameData,
      signal: abortController.signal,
    }).unwrap();

    dispatch(setHints(hints));
  };

  const handleMoveCheckers = (checkerPositions: ICheckerPositions) => {
    dispatch(setGameData({ ...gameData, checkerPositions }));
  };

  useEffect(() => {
    handleGetHint();
  }, [gameData]);

  return (
    <>
      <div className="relative h-screen w-screen overflow-hidden">
        <div className="flex flex-col gap-2 p-2 h-full">
          <div className="relative flex gap-2 p-2 w-full h-full max-h-[50%] border border-base-content rounded-xl items-center overflow-hidden">
            <div className="absolute inset-0 flex flex-col gap-2 p-2 overflow-y-auto">
              <div className="flex gap-2 w-full justify-center items-center">
                <div className="flex flex-col gap-2 max-w-[33%] w-1/3 h-full">
                  <span>Detected Image:</span>
                  {imageUrl ? (
                    <img src={imageUrl || ""} alt="Detected result" />
                  ) : (
                    <div className="flex justify-center items-center w-full h-full overflow-hidden">
                      <span className="loading loading-dots loading-lg"></span>
                      <span>Capturing...</span>
                    </div>
                  )}
                </div>
                <div className="flex flex-col gap-2 max-w-[33%] w-1/3 h-full">
                  <span>Current state:</span>
                  <BackgammonBoard
                    gameData={gameData}
                    onMoveChecker={handleMoveCheckers}
                  />
                </div>
                <div className="flex flex-col gap-2 w-1/3 h-full">
                  {hints && !loading && (
                    <div className="mockup-code h-full">
                      <pre data-prefix=">" className="text-warning">
                        <code>Hints</code>
                      </pre>
                      <pre data-prefix="!" className="text-info">
                        <code>
                          Dices: {gameData.dices.map((dice) => dice.value).join(" ")}
                        </code>
                      </pre>

                      {hints.map((hint) => (
                        <pre
                          key={hint}
                          data-prefix="-"
                          className="text-success"
                        >
                          <code>{hint}</code>
                        </pre>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          <div className="relative flex-1 border border-base-content rounded-xl h-full overflow-hidden">
            <div className="absolute inset-0 flex flex-col gap-2 p-2 overflow-y-auto">
              <div className="flex gap-2 w-full justify-center items-center">
                <WebcamCapture onCapture={handleDetection} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Admin;
