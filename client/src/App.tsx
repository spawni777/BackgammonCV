import { useRef, useState } from "react";
import Editor from "@monaco-editor/react";
import WebcamCapture from "./components/WebcamCapture";
import { useDetectBoardMutation, useGetHintsMutation, useParseBoardMutation } from "./api/backgammon.api";
import { useAppDispatch, useAppSelector } from "./app/hooks";
import { generateEmptyCheckerPositions, selectHints, setGameData, setHints } from "./reducers/backgammon.slice";

const App = () => {
  const dispatch = useAppDispatch();

  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const hints = useAppSelector(selectHints);
  const formattedHints = JSON.stringify(hints, null, 2);

  const [detectBoard] = useDetectBoardMutation();
  const [parseBoard] = useParseBoardMutation();
  const [getHints] = useGetHintsMutation();

  const abortControllerRef = useRef<AbortController | null>(null);

  const handleDetection = async (file: File) => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    const abortController = new AbortController();
    abortControllerRef.current = abortController;

    const formData = new FormData();
    formData.append("image", file);

    dispatch(setGameData(generateEmptyCheckerPositions()));
    dispatch(setHints([]));
    setErrorMessage("");
    setLoading(true);

    try {
      const imageUrl = await detectBoard({
        body: formData,
        signal: abortController.signal,
      }).unwrap();

      if (!imageUrl) {
        throw new Error('Failed to detect board.')
      }

      setImageUrl(imageUrl);

      const gameData = await parseBoard({
        body: formData,
        signal: abortController.signal,
      }).unwrap();

      dispatch(setGameData(gameData));

      const hints = await getHints({
        body: gameData,
        signal: abortController.signal,
      }).unwrap();

      dispatch(setHints(hints));
    } catch (error) {
      const errorMessage = JSON.stringify(error)
      console.error("Error during detection, parsing or getting hints:", error);
      setErrorMessage(errorMessage)
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="relative h-screen w-screen overflow-hidden">
        <div className="flex flex-col gap-2 p-2 h-full">
          <WebcamCapture
            onCapture={handleDetection}
          />

          <div className="relative flex-1 border border-base-content rounded-xl h-full overflow-hidden">
            <div className="absolute inset-0 flex flex-col gap-2 p-2 overflow-y-auto">
              {errorMessage && <span className="text-error">{errorMessage}</span>}
              <div className="flex gap-2 w-full justify-center items-center">
                {loading ? (
                  <div className="flex gap-2 items-center">
                    <span className="loading loading-dots loading-lg"></span>
                    <span>Loading...</span>
                  </div>
                ) : !imageUrl ? (
                  <div className="flex gap-2 items-center">
                    <span className="loading loading-dots loading-lg"></span>
                    <span>Capturing...</span>
                  </div>
                ) : (
                  <>
                    <div className="flex flex-col gap-2">
                      <span>Detected Image:</span>
                      <img src={imageUrl} alt="Detected result" />
                    </div>

                    <div className="flex flex-col gap-2 w-full h-full">
                      <span>Hints:</span>
                      {hints && !loading && (
                        <Editor
                          defaultLanguage="json"
                          value={formattedHints}
                          onChange={(value) => setHints(value || "")}
                          theme="vs-dark"
                          options={{
                            automaticLayout: true,
                            formatOnType: true,
                            formatOnPaste: true,
                          }}
                        />
                      )}
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default App;
