from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from model import TrainedModel
import base64
from io import BytesIO
from PIL import Image

api = FastAPI()

trained_model = TrainedModel()


class PredictionRequest(BaseModel):
    image: str
    filename: Optional[str] = None


@api.post("/model/predict")
def predict(request: PredictionRequest):
    try:
        if request.filename is None:
            return (trained_model
                    .predict(from_base64(request.image))
                    .to_dict(orient='records'))
        else:
            return (trained_model
                    .predict_test_image(from_base64(request.image), f"{request.filename}.png")
                    .to_dict(orient='records'))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def from_base64(base64_str: str) -> Image:
    image_data = base64.b64decode(base64_str)
    image_io = BytesIO(image_data)
    image = Image.open(image_io)
    return image
