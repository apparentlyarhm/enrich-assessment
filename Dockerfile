# This image is for the FastAPI app.

# Some deps requires whole build-essential for compilation of wheels with C-based python modules. 
# Throwing away compilation environment saves space. If there is no compilation and wheels are downloaded 'as-is',
# I see not benefits for multistage. 

FROM python:3.11-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY req.txt . 
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r req.txt

COPY ./src ./src
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "1234"]