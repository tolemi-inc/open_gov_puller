FROM python:3.12-bookworm

RUN echo $PATH

WORKDIR /opt/open_gov_puller

COPY requirements.txt /opt/open_gov_puller
RUN pip install -r requirements.txt
RUN python -m playwright install --with-deps

# copy the script
COPY open_gov_puller /opt/open_gov_puller

# add the script callers to path
ENV PATH="/opt/open_gov_puller/bin:$PATH"
