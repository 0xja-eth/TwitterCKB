# 使用Python官方镜像
FROM python:3.11
LABEL authors="GaryMa"

# set workdir
WORKDIR /app

# copy
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
