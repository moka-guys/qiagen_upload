FROM python:3.10.6

LABEL author="Rachel Duffin" \
    maintainer="rachel.duffin2@nhs.net"

RUN mkdir -p /qiagen_upload /qiagen_upload
RUN mkdir -p /qiagen_upload/get_user_code
RUN mkdir -p /qiagen_upload/qiagen_upload
ADD ./requirements.txt /qiagen_upload/
RUN pip3 install -r /qiagen_upload/requirements.txt
ADD ./*.py /qiagen_upload/
ADD ./qiagen_upload/* /qiagen_upload/qiagen_upload/
ADD ./get_user_code/* /qiagen_upload/get_user_code/
ADD /.git /qiagen_upload/
ADD ./templates/ /qiagen_upload/templates/
WORKDIR /qiagen_upload/
ENTRYPOINT [ "python3","-m"]