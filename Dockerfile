FROM python:3.9
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH
WORKDIR $HOME/app
COPY --chown=user . $HOME/app
COPY ./requirements.txt ~/app/requirements.txt
RUN pip install -r requirements.txt
COPY . .
RUN mkdir -p $HOME/app/data && chown -R user:user $HOME/app/data
COPY ./data/airbnb.pdf ~/app/data/airbnb.pdf
CMD ["chainlit", "run", "app.py", "--port", "7860"]