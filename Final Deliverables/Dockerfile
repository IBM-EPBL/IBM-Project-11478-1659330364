FROM python:buster

WORKDIR /python-expense

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "-m" , "flask", "run"]