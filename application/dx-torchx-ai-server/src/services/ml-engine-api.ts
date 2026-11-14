import axios from 'axios';

const host = process.env.ML_API_HOST || 'localhost';
const port = process.env.ML_API_PORT || '3001';

export const getPrediction = async (base64image: string, filename?: string) => {
  try {
    const response = await axios.post(`http://${host}:${port}/model/predict`, {
      image: base64image,
      filename,
    });
    return response.data;
  } catch (error) {
    console.error('Error calling prediction service:', error);
  }
  return null;
};