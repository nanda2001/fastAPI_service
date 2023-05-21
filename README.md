# Hugging Face to v2 Inference Protocol Converter

The Hugging Face to v2 Inference Protocol Converter is a project designed to convert payload from Hugging Face Inference API format to v2 Inference Protocol API format.

## Features

- Converts payload from Hugging Face Inference API format to v2 Inference Protocol API format and returning predicted value
- FastAPI service that accepts input in HF format along with additional details.
- Supports four pipelines: Zero-shot Classification, Text Generation, Token Classification, and Object Detection.

## Start the FastAPI service:

shell

''' uvicorn main:app --reload '''


The service will be available at http://localhost:8000 by default.

Make a POST request to the /predict endpoint with the necessary payload in HF format and additional details. The payload should include the following fields:

## Example payload:

'''{
  "hf_pipeline": "zero-shot-classification",
  "model_URL": "https://your-model-url.com",
  "input": "Your input text",
  "parameters": {
    "param1": "value1",
    "param2": "value2"
  }
}'''

Note: Ensure the values are replaced with the actual data.

The service will convert the payload to v2 Inference Protocol API format and