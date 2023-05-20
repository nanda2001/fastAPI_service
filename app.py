from fastapi import FastAPI
from pydantic import BaseModel
import re
import httpx

def is_valid_url(url):
    regex_pattern = r"^(http|https|ftp)://[^\s/$.?#].[^\s]*$"
    return re.match(regex_pattern, url) is not None


def zero_shot_classification(input_hf):
    #Validate input_hf

    #Convert to V2_input 
    v2_input = {
        'inputs': [
            # Inputs
            {
                'name': 'array_inputs',
                'datatype': 'STRING',
                'shape': [-1],
                'parameters': {'content_type': 'str'},
                'data': input_hf['inputs']
            },
            # candidate_labels
            {
                'name': 'candidate_labels',
                'datatype': 'STRING',
                'shape': [len(input_hf['parameters']['candidate_labels'])],
                'parameters': {'content_type': 'str'},
                'data': input_hf['parameters']['candidate_labels']
            }
        ]
    }
    #Additional parameters

    # multi_label
    if('multi_lasbel' in input_hf['parameters']):
        v2_input['inputs'].append(
            {
                'name': 'multi_label',
                'datatype': 'BOOL',
                'shape': [-1],
                'parameters': {'content_type': 'str'},
                'data': f"{input_hf['parameters']['multi_label']}"
            }
        )

    if('options' in input_hf):
        # use_cache
        if('use_cache' in input_hf['options']):
            v2_input['inputs'].append(
            {
                'name': 'use_cache',
                'datatype': 'BOOL',
                'shape': [-1],
                'parameters': {'content_type': 'str'},
                'data': f"{input_hf['options']['use_cache']}"
            }
        )
        
        # wait_for_model
        if('wait_for_model' in input_hf['options']):
            v2_input['inputs'].append(
            {
                'name': 'wait_for_model',
                'datatype': 'BOOL',
                'shape': [-1],
                'parameters': {'content_type': 'str'},
                'data': f"{input_hf['options']['wait_for_model']}"
            }
        )
    
    return v2_input


def token_classification(input_hf):
    #Validate input_hf

    #Convert to V2_input 
    v2_input = {
        'inputs': [
            # Inputs
            {
                'name': 'args',
                'datatype': 'STRING',
                'shape': [-1],
                'parameters': {'content_type': 'str'},
                'data': input_hf['inputs']
            }
        ]
    }
    #TODO: Additional parameters
    '''
    # aggregation_strategy
    # use_cache
    # wait_for_model
    '''
    return v2_input


def text_generation(input_hf):
    #Validate input_hf

    #Convert to V2_input 
    v2_input = {
    "inputs": [
        {
        "name": "array_inputs",
        "shape": [-1],
        "datatype": "BYTES",
        "data": input_hf['inputs']
        }
    ]
    }
    if('parameters' in input_hf):
        # top_k
        if('top_k' in input_hf['parameters']):
            v2_input['inputs'].append(
            {
            "name": "top_k",
            "shape": [-1],
            "datatype": "BYTES",
            "data": [f"{input_hf['parameters']['top_k']}"],
            "parameters": {
                "content_type": "hg_json"
            }
        }
        )
        # min_new_tokens
        if('min_new_tokens' in input_hf['parameters']):
            v2_input['inputs'].append(
            {
            "name": "min_new_tokens",
            "shape": [-1],
            "datatype": "BYTES",
            "data": [f"{input_hf['parameters']['min_new_tokens']}"],
            "parameters": {
                "content_type": "hg_json"
            }
        }
        )
        
        # temperature
        if('temperature' in input_hf['parameters']):
            v2_input['inputs'].append(
            {
            "name": "temperature",
            "shape": [-1],
            "datatype": "BYTES",
            "data": [f"{float(input_hf['parameters']['temperature'])}"],
            "parameters": {
                "content_type": "hg_json"
            }
        }
        )
        
        # max_new_tokens
        if('max_new_tokens' in input_hf['parameters']):
            v2_input['inputs'].append(
            {
            "name": "max_new_tokens",
            "shape": [-1],
            "datatype": "BYTES",
            "data": [f"{input_hf['parameters']['max_new_tokens']}"],
            "parameters": {
                "content_type": "hg_json"
            }
        }
        )  
        
        # num_return_sequences
        if('num_return_sequences' in input_hf['parameters']):
            v2_input['inputs'].append(
            {
            "name": "num_return_sequences",
            "shape": [-1],
            "datatype": "BYTES",
            "data": [f"{input_hf['parameters']['num_return_sequences']}"],
            "parameters": {
                "content_type": "hg_json"
            }
        }
        )

    return v2_input


def object_detection(input_hf):
    v2_input = {
        # input
        'inputs': [
            {
                'name': 'inputs',
                'shape': [-1],
                'datatype': "BYTES",
                'data': input_hf['inputs']
            }
        ]
    }
    # Setting content type according to input which can be BYTES str of URL str
    if(is_valid_url(v2_input['inputs'][0]['data'])):
        v2_input['inputs'][0]['parameters'] = {'content_type': 'str'}
    else:
        v2_input['inputs'][0]['parameters'] = {'content_type': 'pillow_image'}

    return v2_input

app = FastAPI()

class PredictionRequest(BaseModel):
    hf_pipeline: str
    model_deployed_url: str
    inputs: str
    parameters: dict

@app.post("/predict")
async def predict(payload: PredictionRequest):
    
    # Extract the values from the payload
    URL=payload.model_deployed_url
    input_dict = {
        'inputs': payload.inputs,
        'parameters': payload.parameters
    }
    if(payload.hf_pipeline=="token-classification"):
        v2_inp =  token_classification(input_dict)
    if(payload.hf_pipeline=="zero-shot-classification"):
        v2_inp =  zero_shot_classification(input_dict)
    if(payload.hf_pipeline=="object-detection"):
        v2_inp =  object_detection(input_dict)
    if(payload.hf_pipeline=="text-generation"):
        v2_inp =  text_generation(input_dict)

    async with httpx.AsyncClient() as client:
        timeout = httpx.Timeout(40.0, read=None)
        response = await client.post(URL, json=v2_inp, timeout=timeout)
    v2_output = response
    return v2_output.json()
