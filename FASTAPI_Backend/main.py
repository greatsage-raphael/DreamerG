from http.client import HTTPException
from fastapi import FastAPI, UploadFile, File
import shutil
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


from fastapi.middleware.cors import CORSMiddleware
import requests
import os
import sys

# Assuming your script is within the project directory and you want to add the project directory
project_directory = os.path.dirname(os.path.abspath(__file__))
if project_directory not in sys.path:
    sys.path.append(project_directory)

from gradio_client import Client, file

# Example model for data validation
from pydantic import BaseModel
class Prompt(BaseModel):
    message: str


import google.generativeai as genai

genai.configure(api_key="YOUR_API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
    expose_headers=["X-New-Prompt"]  # Expose custom headers

)

UPLOAD_DIRECTORY = "./uploads"
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

app.mount("/static", StaticFiles(directory="uploads"), name="static")

def safe_header_value(value):
    """Ensure the header value is a single line, ASCII, and stripped of any leading/trailing whitespace."""
    if value is not None:
        # Remove newlines and replace non-ASCII characters
        value = value.replace('\n', ' ').replace('**', '').strip().encode('ascii', 'ignore').decode('ascii')
    return value

def delete_contents_of_output(directory_path='output'):
    # Ensure the directory exists
    if not os.path.exists(directory_path):
        print("Directory does not exist")
        return

    # Iterate through each item in the directory
    for item_name in os.listdir(directory_path):
        item_path = os.path.join(directory_path, item_name)

        # Check if the item is a file or a directory
        if os.path.isfile(item_path):
            os.remove(item_path)  # Remove the file
        else:
            shutil.rmtree(item_path)  # Remove the directory and all its contents

    print("All files and folders inside the 'output' directory have been deleted.")


def download_and_save_image(image_url, file_path):
    try:
        # Send a GET request to the image URL
        response = requests.get(image_url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Write the image data to a file
        with open(file_path, 'wb') as file:
            file.write(response.content)
        return True
    except requests.RequestException as e:
        print(f"Error downloading the image: {e}")
        return False
    except IOError as e:
        print(f"Error saving the image: {e}")
        return False

def enhance_prompt_gemini(original_promt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(f"Expand this brief object description into a detailed, vivid prompt for an image generator like stable diffusion. Make sure the object is on flat ground. Make sure the image is suitable for a image-to-3D model generator: {original_promt}")
    
    return response.text


def generate_3D_model(filepath):
    print("Generate 3D model")
    client = Client(src="TencentARC/InstantMesh",output_dir="C:/Users/Kurst/Downloads/Gemini/FASTAPI_Backend/output/")
    result = client.predict(
            input_image=file(filepath),
            do_remove_background=True,
            api_name="/preprocess"
    )
    result = client.predict(
		input_image=file(result),
		sample_steps=75,
		sample_seed=42,
		api_name="/generate_mvs"
    )
    result = client.predict(
		api_name="/make3d"
    )
    return result[1]

@app.post("/text-generate-model-gemini/")
async def process_image(prompt: Prompt):
    delete_contents_of_output()

    try:
        new_prompt = enhance_prompt_gemini(prompt.message)
        new_prompt2 = f'{new_prompt}. In addition, make sure that the background of the image is a single color. Finally, make sure the image is realistic 3d render of {prompt.message}.'
        print(new_prompt2)
        prompt3 = f'Generate a realistic 3d render image of {prompt.message}.In addition, make sure that the background of the image is a single color.'
        SDXL = Client("ByteDance/SDXL-Lightning",output_dir="C:/Users/Kurst/Downloads/Gemini/FASTAPI_Backend/output/")
        result = SDXL.predict(
                prompt3,	# str  in 'Enter your prompt (English)' Textbox component
                "8-Step",	# Literal['1-Step', '2-Step', '4-Step', '8-Step']  in 'Select inference steps' Dropdown component
                api_name="/generate_image"
        )
        print(result)
        filepath = result
        model_path = generate_3D_model(filepath)
        safe_prompt = safe_header_value(new_prompt2)
        headers_value = {"X-New-Prompt": safe_prompt}  # Sending new_prompt2 in a custom header
        print(headers_value)

        print("Finish")

        return FileResponse(model_path, headers=headers_value, media_type='application/octet-stream', filename="model.glb")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
