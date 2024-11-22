import uvicorn
from fastapi import FastAPI # need python-multipart
from app import views
from app.database import engine

app = FastAPI(title="AdviNow Interview Challenge", version="1.6")
# print("Database connected successfully!")
app.include_router(views.router)
# try:
#     connection = engine.connect()
#     print("Database connected successfully!")
#     connection.close()
# except Exception as e:
#     print("Failed to connect to the database:", e)

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8013)
    