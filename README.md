# DreamerG

A web application to generate 3D model from text input fuel by Google Gemini A.I .

## Installation

To start the react frontend do as follow.

```bash
#start at root folder
cd React_Frontend
npm install
npm run dev
```

To start the FASTAPI backend end do as follow
```bash
#start at root folder
cd FASTAPI_Backend
pip install -r requirements.txt
```
Then add your Gemini Google A.I API key on line 28 in the main.py
```python
genai.configure(api_key="YOUR_API_KEY")
```
Finally start the backend server 
```bash
uvicorn main:app --reload
```

## License

[MIT](https://choosealicense.com/licenses/mit/)