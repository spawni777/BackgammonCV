import { useRef, useState, useEffect } from "react";
import Webcam from "react-webcam";
import { base64ToBlob } from "../utils";

const PIXEL_SCORE_THRESHOLD = 20;
const MOTION_SCORE_THRESHOLD = 5000;
const PIXEL_SKIP = 10;

const WebcamCapture = ({ onCapture }: { onCapture?: (file: File) => void }) => {
  const webcamRef = useRef<Webcam>(null);
  const canvasRef = useRef<HTMLCanvasElement>(document.createElement("canvas"));
  const motionCanvasRef = useRef<HTMLCanvasElement>(
    document.createElement("canvas")
  );
  const prevFrameDataRef = useRef<Uint8ClampedArray>();

  const [screenshotSrc, setScreenshotSrc] = useState<string | null>(null);
  const [shouldCaptureScreenshot, setShouldCaptureScreenshot] =
    useState<boolean>(false);
  const [isMotionDetected, setIsMotionDetected] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [ready, setReady] = useState<boolean>(false);

  const captureScreenshot = async () => {
    if (webcamRef.current) {
      const screenshot = webcamRef.current.getScreenshot({
        width: 640,
        height: 480,
      });

      if (screenshot) {
        if (onCapture) {
          const blob = base64ToBlob(screenshot);
          const file = new File([blob], "screenshot.jpg");

          onCapture(file);
        }

        setScreenshotSrc(screenshot);
      }
    }
  };

  const detectMotion = () => {
    if (!webcamRef.current) return;

    const canvas = canvasRef.current;
    const motionCanvas = motionCanvasRef.current;

    const ctx = canvas.getContext("2d", { willReadFrequently: true });
    const motionCtx = motionCanvas.getContext("2d", {
      willReadFrequently: true,
    });

    const video = webcamRef.current.video as HTMLVideoElement;
    const { width, height } = video.getBoundingClientRect();

    if (width === 0 || height === 0) return;

    if (canvas.width !== width || canvas.height !== height) {
      canvas.width = width;
      canvas.height = height;
      motionCanvas.width = width;
      motionCanvas.height = height;
    }

    ctx?.drawImage(video, 0, 0, width, height);

    const currentFrameData = ctx?.getImageData(0, 0, width, height)?.data;
    const prevFrameData = prevFrameDataRef.current || [];

    if (currentFrameData && prevFrameData) {
      const length = currentFrameData.length;
      const motionPixels = new Uint8ClampedArray(length);

      let motionPixelCount = 0;

      for (let i = 0; i < length; i += 4 * PIXEL_SKIP) {
        const rDiff = Math.abs(currentFrameData[i] - prevFrameData[i]);
        const gDiff = Math.abs(currentFrameData[i + 1] - prevFrameData[i + 1]);
        const bDiff = Math.abs(currentFrameData[i + 2] - prevFrameData[i + 2]);

        if (
          rDiff > PIXEL_SCORE_THRESHOLD ||
          gDiff > PIXEL_SCORE_THRESHOLD ||
          bDiff > PIXEL_SCORE_THRESHOLD
        ) {
          motionPixels[i] = 255;
          motionPixels[i + 1] = 0;
          motionPixels[i + 2] = 0;
          motionPixels[i + 3] = 255;

          motionPixelCount++;
        } else {
          motionPixels[i + 3] = 0;
        }
      }

      setIsMotionDetected(motionPixelCount > MOTION_SCORE_THRESHOLD);

      const motionImageData = new ImageData(motionPixels, width, height);

      motionCtx?.putImageData(motionImageData, 0, 0);
    }

    prevFrameDataRef.current = currentFrameData;
  };

  useEffect(() => {
    const interval = setInterval(detectMotion, 200);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (!ready) return;

    setTimeout(() => captureScreenshot(), 200);
  }, [ready]);

  useEffect(() => {
    if (shouldCaptureScreenshot && !isMotionDetected) {
      captureScreenshot();
      setShouldCaptureScreenshot(false);
    }

    if (!isMotionDetected) {
      setShouldCaptureScreenshot(true);
    }
  }, [shouldCaptureScreenshot, isMotionDetected]);

  return (
    <div className="flex flex-col gap-2 p-2 w-full border border-base-content rounded-xl items-center overflow-hidden">
      <button className="btn btn-success" onClick={captureScreenshot}>Manual capture</button>
      <div className="flex gap-2 w-full justify-around">
        <div className="flex flex-col gap-2 max-w-[50%] items-center overflow-hidden">
          <span>Current video</span>
          <div className="relative flex">
            <Webcam
              audio={false}
              ref={webcamRef}
              screenshotFormat="image/jpeg"
              onUserMediaError={(error) =>
                setErrorMessage(`Error accessing webcam: ${error}`)
              }
              onUserMedia={() => setReady(true)}
            />
            <canvas className="absolute inset-0" ref={motionCanvasRef}></canvas>
            {errorMessage ?
              <span className="text-error self-center">{errorMessage}</span>
              : (
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2">
                  {isMotionDetected ? (
                    <span className="text-warning">Motion Detected!</span>
                  ) : (
                    <span>No Motion</span>
                  )}
                </div>
              )
            }
          </div>
        </div>
        <div className="flex flex-col gap-2 max-w-[50%] items-center overflow-hidden">
          <span>Captured</span>
          {screenshotSrc && <img src={screenshotSrc} alt="Captured" />}
        </div>
      </div>
    </div>
  );
};

export default WebcamCapture;
