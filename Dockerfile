FROM python:3.11.3
ENV PYTHONUNBUFFERED True

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r  requirements.txt

ENV APP_HOME /root
WORKDIR $APP_HOME
COPY /autotx $APP_HOME/autotx
COPY .deploy.env $APP_HOME/.env

EXPOSE 8080
CMD ["uvicorn", "autotx.server:app", "--host", "0.0.0.0", "--port", "8080"]