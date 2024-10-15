import { useState } from 'react';
import '@/assets/styles/home.css';
import Editor from '@monaco-editor/react';

function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [gameData, setGameData] = useState<string>("");
  const [hints, setHints] = useState<string>("");
  const [loading, setLoading] = useState(false);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files ? event.target.files[0] : null;

    if (file && validateFile(file)) {
      setSelectedFile(file);
      setError(null);
    } else {
      setSelectedFile(null);
      setError('Please upload a valid image (PNG, JPG, JPEG).');
    }
  };

  const validateFile = (file: File) => {
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg'];
    return allowedTypes.includes(file.type);
  };

  const handleDetection = async () => {
    const formData = new FormData();
    formData.append('image', selectedFile!);
    setGameData("");
    setHints("");

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/backgammon/detect`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const blob = await response.blob();
        const imageUrl = URL.createObjectURL(blob);
        setImageUrl(imageUrl);
      } else {
        alert('Failed to upload image.');
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('An error occurred while uploading the file.');
    }
  };

  const handleParsing = async () => {
    const formData = new FormData();
    formData.append('image', selectedFile!);
    setHints("");
    
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/backgammon/parse`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        setGameData(JSON.stringify(result, null, 2));
      } else {
        alert('Failed to upload image.');
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('An error occurred while uploading the file.');
    }
  };

  const handleGetHints = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/backgammon/hint`, {
        method: 'POST',
        body: gameData,
        headers: {
          "content-type": "application/json"
        }
      });

      if (response.ok) {
        const hints = await response.json();
        setHints(JSON.stringify(hints, null, 2));
      } else {
        alert('Failed to get hints.');
      }
    } catch (error) {
      console.error('Error getting hints:', error);
      alert('An error occurred while getting hints.');
    }
  };

  const onSubmit = async () => {
    if (!selectedFile) {
      alert('Please select a file first!');
      return;
    }

    setLoading(true);

    try {
      await Promise.all([handleDetection(), handleParsing()]);
    } finally {
      setLoading(false);
    }
  };

  const onGetHints = async () => {
    await handleGetHints();
  };

  return (
    <>
      <div className="home">
        <input type="file" accept="image/*" onChange={handleFileChange} />
        {error && <p style={{ color: 'red' }}>{error}</p>}

        <button onClick={onSubmit} disabled={!selectedFile || loading}>
          {loading ? 'Loading...' : 'Upload Image'}
        </button>

        {imageUrl && !loading && (
          <div>
            <h3>Detected Image:</h3>
            <img src={imageUrl} alt="Detected result" />
          </div>
        )}

        {!!gameData.length && !loading && (
          <>
            <Editor
              height="400px"
              defaultLanguage="json"
              value={gameData}
              onChange={(value) => setGameData(value || '')}
              theme="vs-dark"
              options={{
                automaticLayout: true,
                formatOnType: true,
                formatOnPaste: true,
              }}
            />
            <button onClick={onGetHints} disabled={loading}>
              {loading ? 'Loading...' : 'Get hints'}
            </button></>
        )}
        {hints && !loading && (
          <Editor
            height="400px"
            defaultLanguage="json"
            value={hints}
            onChange={(value) => setHints(value || '')}
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
  );
}

export default App;
