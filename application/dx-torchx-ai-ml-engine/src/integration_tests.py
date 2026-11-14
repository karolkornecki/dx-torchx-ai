import pytest
import pytest_asyncio
import math
from httpx import AsyncClient
from server import api


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(app=api, base_url="http://test") as ac:
        yield ac


def read_base64_image(filepath: str) -> str:
    with open(filepath, 'r', encoding='utf-8') as file:
        return file.read()


def floats_close(a: float, b: float, eps: float = 1e-3) -> bool:
    return math.isclose(a, b, abs_tol=eps)


EPSILON = 1e-2

expected_predictions = [
    {'class_name': 'Atelectasis', 'y_prob': 0.090000, 'y_predicted': 0, 'y_true': 0, 'threshold': 0.094},
    {'class_name': 'Cardiomegaly', 'y_prob': 0.262000, 'y_predicted': 1, 'y_true': 0, 'threshold': 0.057},
    {'class_name': 'Effusion', 'y_prob': 0.050000, 'y_predicted': 0, 'y_true': 0, 'threshold': 0.106},
    {'class_name': 'Infiltration', 'y_prob': 0.049000, 'y_predicted': 0, 'y_true': 0, 'threshold': 0.166},
    {'class_name': 'Mass', 'y_prob': 0.013000, 'y_predicted': 0, 'y_true': 0, 'threshold': 0.053},
    {'class_name': 'Nodule', 'y_prob': 0.045000, 'y_predicted': 0, 'y_true': 0, 'threshold': 0.062},
    {'class_name': 'Pneumonia', 'y_prob': 0.004000, 'y_predicted': 0, 'y_true': 0, 'threshold': 0.012},
    {'class_name': 'Pneumothorax', 'y_prob': 0.002000, 'y_predicted': 0, 'y_true': 0, 'threshold': 0.062},
    {'class_name': 'Consolidation', 'y_prob': 0.013000, 'y_predicted': 0, 'y_true': 0, 'threshold': 0.046},
    {'class_name': 'Edema', 'y_prob': 0.001000, 'y_predicted': 0, 'y_true': 0, 'threshold': 0.017},
    {'class_name': 'Emphysema', 'y_prob': 0.010000, 'y_predicted': 0, 'y_true': 0, 'threshold': 0.023},
    {'class_name': 'Fibrosis', 'y_prob': 0.014000, 'y_predicted': 0, 'y_true': 0, 'threshold': 0.015},
    {'class_name': 'Pleural_Thickening', 'y_prob': 0.031000, 'y_predicted': 0, 'y_true': 0, 'threshold': 0.044},
    {'class_name': 'Hernia', 'y_prob': 0.005000, 'y_predicted': 1, 'y_true': 0, 'threshold': 0.002},
]


@pytest.mark.asyncio
async def test_should_return_actual_prediction_with_true_label_for_known_image_from_test_dataset(client):
    base64_image = read_base64_image("test_data/image.txt")
    response = await client.post("/model/predict", json={"image": base64_image, "filename": '00000007_000'})
    assert response.status_code == 200
    actual = response.json()
    assert isinstance(actual, list)
    assert len(actual) == len(expected_predictions)

    for actual_item, expected_item in zip(actual, expected_predictions):
        assert actual_item["class_name"] == expected_item["class_name"], \
            f"Class name mismatch: {actual_item['class_name']} != {expected_item['class_name']}"
        assert floats_close(actual_item["y_prob"], expected_item["y_prob"]), \
            f"y_prob mismatch for {actual_item['class_name']}"
        assert floats_close(actual_item["threshold"], expected_item["threshold"]), \
            f"threshold mismatch for {actual_item['class_name']}"
        assert actual_item["y_predicted"] == expected_item["y_predicted"], \
            f"y_predicted mismatch for {actual_item['class_name']}"
        assert actual_item["y_true"] == expected_item["y_true"], \
            f"y_true mismatch for {actual_item['class_name']}"


@pytest.mark.asyncio
async def test_should_return_actual_prediction_without_true_label_for_some_image(client):
    base64_image = read_base64_image("test_data/image.txt")
    response = await client.post("/model/predict", json={"image": base64_image})
    assert response.status_code == 200
    actual = response.json()
    assert isinstance(actual, list)
    assert len(actual) == len(expected_predictions)

    for actual_item, expected_item in zip(actual, expected_predictions):
        assert actual_item["class_name"] == expected_item["class_name"], \
            f"Class name mismatch: {actual_item['class_name']} != {expected_item['class_name']}"
        assert floats_close(actual_item["y_prob"], expected_item["y_prob"]), \
            f"y_prob mismatch for {actual_item['class_name']}"
        assert floats_close(actual_item["threshold"], expected_item["threshold"]), \
            f"threshold mismatch for {actual_item['class_name']}"
        assert actual_item["y_predicted"] == expected_item["y_predicted"], \
            f"y_predicted mismatch for {actual_item['class_name']}"
        assert "y_true" not in actual_item


@pytest.mark.asyncio
async def test_should_return_error_when_file_does_not_exist_in_test_dataset(client):
    base64_image = read_base64_image("test_data/image.txt")
    response = await client.post("/model/predict", json={"image": base64_image, "filename": "unknown_file_name"})
    assert response.status_code == 400
    assert response.json()["detail"] == "unknown_file_name.png"


@pytest.mark.asyncio
async def test_should_return_error_when_image_argument_is_not_valid_base64_encoded_image(client):
    response = await client.post("/model/predict", json={"image": "x", "filename": "unknown_file_name"})
    assert response.status_code == 400
    assert "Invalid base64-encoded string" in response.json()["detail"]
