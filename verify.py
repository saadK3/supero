from dotenv import load_dotenv
import os

load_dotenv()

print(os.getenv("DATABASE_URL"))
print(os.getenv("REDIS_URL"))