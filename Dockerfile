FROM python:3

WORKDIR /projet_webapp

COPY ./requirements.txt /projet_webapp/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /projet_webapp/requirements.txt

COPY . .

EXPOSE 80

CMD ["uvicorn", "webapp.main:app", "--host","0.0.0.0", "--port", "80"]
#CMD ["fastapi", "run", "webapp/main.py","--proxy-headers", "--port", "80"]
