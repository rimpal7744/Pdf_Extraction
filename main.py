from fastapi import FastAPI, File, UploadFile
from algorithmm import main
import uvicorn
import os
app = FastAPI()


@app.post("/upload-file/")
async def create_upload_file(file: UploadFile = File(...)):
    file_location = f"{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    result=main(file_location)
    os.remove(file_location)
    return result



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6000)

