FROM docker:cli
RUN apk add --no-cache python3 py3-flask py3-requests
COPY app.py /app/
WORKDIR /app
EXPOSE 6006
CMD ["python3", "app.py"]
