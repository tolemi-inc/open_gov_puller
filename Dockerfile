#CONTAINER TEMPLATE
FROM python:3.9-slim-bookworm

RUN echo $PATH

WORKDIR /opt/open_gov_puller

#install requirements
COPY requirements.txt /opt/open_gov_puller
RUN pip install -r requirements.txt

# copy the script
COPY open_gov_puller /opt/open_gov_puller

# add the script callers to path
ENV PATH="/opt/open_gov_puller/bin:$PATH"