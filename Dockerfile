FROM python:3.6

# Install pytesseract on system
RUN apt-get update
RUN apt-get install -y tesseract-ocr
RUN apt-get install -y libtesseract-dev

RUN mkdir -p /opt/services/vectorai/src
WORKDIR /opt/services/vectorai/src


COPY . /opt/services/vectorai/src

RUN pip3 install -r requirements.txt
RUN cd vectorai && python3 manage.py collectstatic --no-input 