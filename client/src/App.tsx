import { useState } from 'react';
import '@/assets/styles/home.css';

function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [imageUrl, setImageUrl] = useState<string | null>(null); // To store and display image URL

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

  const handleSubmit = async () => {
    if (!selectedFile) {
      alert('Please select a file first!');
      return;
    }

    const formData = new FormData();
    formData.append('image', selectedFile);

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/backgammon/parse`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const blob = await response.blob(); // Get the image blob
        const imageUrl = URL.createObjectURL(blob); // Create a URL for the blob
        setImageUrl(imageUrl); // Set the image URL to display it
      } else {
        alert('Failed to upload image.');
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('An error occurred while uploading the file.');
    }
  };

  return (
    <>
      <div className="home">
        <input type="file" accept="image/*" onChange={handleFileChange} />
        {error && <p style={{ color: 'red' }}>{error}</p>}
        <button onClick={handleSubmit} disabled={!selectedFile}>Upload Image</button>
        
        {/* Display the image here */}
        {imageUrl && (
          <div>
            <h3>Detected Image:</h3>
            <img src={imageUrl} alt="Detected result" />
          </div>
        )}
      </div>
    </>
  );
}

export default App;
