FROM amazon/aws-lambda-python:3.8

RUN yum update -y

COPY requirements.txt ./
COPY *.py ./

RUN pip install -r requirements.txt

CMD ["app.lambda_handler"]