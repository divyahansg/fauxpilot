FROM python:3.10-slim-buster

# Update default packages
RUN apt-get update

# Get Ubuntu packages
RUN apt-get install -y \
    build-essential \
    curl \
    git \
    nginx

# Update new packages
RUN apt-get update

ENV PATH="/root/.cargo/bin:${PATH}"

# Get Rust
RUN curl https://sh.rustup.rs -sSf | bash -s -- -y

RUN git clone https://github.com/divyahansg/mosec.git && \
    cd mosec && \
    make release

WORKDIR /python-docker

COPY copilot_proxy/requirements.txt requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt

COPY copilot_proxy .

EXPOSE 5000

CMD ["mosec.sh"]
