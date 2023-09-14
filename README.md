# Fastapisample
## Running this project
- Connecting to the MySQL Database
```sh
touch .env
echo "URL_DATABASE = '<db_url>'">> .env
```  
- Creating a virtual environment
```sh
python3 -m venv <env name>
```
- Installing dependencies
```sh
source <env_name>/bin/activate
pip install -r requirements.txt
```
- Running the server
```sh
uvicorn main:app --reload
```
