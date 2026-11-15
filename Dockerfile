FROM ubuntu:22.04
RUN apt-get update && apt-get install -y openjdk-11-jdk python3-pip wget
RUN pip3 install fastapi uvicorn python-multipart
WORKDIR /app
RUN wget https://ghfast.top/https://github.com/iBotPeaches/Apktool/releases/download/v2.9.3/apktool_2.9.3.jar -O apktool.jar
RUN wget https://ghfast.top/https://github.com/patrickfav/uber-apk-signer/releases/download/v1.3.0/uber-apk-signer-1.3.0.jar -O signer.jar
COPY main.py .
EXPOSE 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
