FROM python:latest

ENV http_proxy http://wwwproxy.unimelb.edu.au:8000
ENV https_proxy http://wwwproxy.unimelb.edu.au:8000

WORKDIR /backend
ADD . /backend
RUN pip install -r requirements.txt
EXPOSE 8080
CMD [ "python","manage.py","runserver","0.0.0.0:8080" ]