import { useState } from 'react';
import '@/assets/styles/home.css';
import Editor from '@monaco-editor/react';

function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [positions, setPositions] = useState("");
  const [loading, setLoading] = useState(false); // State for loading

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

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/backgammon/parse`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        setPositions(JSON.stringify(result.positions, null, 2));
      } else {
        alert('Failed to upload image.');
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('An error occurred while uploading the file.');
    }
  };

  const handleSubmit = async () => {
    if (!selectedFile) {
      alert('Please select a file first!');
      return;
    }

    setLoading(true); // Set loading to true when the request starts

    try {
      await Promise.all([handleDetection(), handleParsing()]);
    } finally {
      setLoading(false); // Set loading to false when the request completes
    }
  };

  return (
    <>
      <div className="home">
        <input type="file" accept="image/*" onChange={handleFileChange} />
        {error && <p style={{ color: 'red' }}>{error}</p>}

        {/* Button with loading state */}
        <button onClick={handleSubmit} disabled={!selectedFile || loading}>
          {loading ? 'Loading...' : 'Upload Image'}
        </button>

        {/* Display the image */}
        {imageUrl && !loading && (
          <div>
            <h3>Detected Image:</h3>
            <img src={imageUrl} alt="Detected result" />
          </div>
        )}

        {!!positions.length && !loading && (
          <Editor
            height="400px"
            defaultLanguage="json"
            value={positions}
            onChange={(value) => setPositions(value || '')}
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
