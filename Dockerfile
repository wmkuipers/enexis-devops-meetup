FROM python:3.10.11-slim-buster
LABEL maintainer="willem.kuipers@enexis.nl"

ARG GITLAB_USER_EMAIL
ARG CI_COMMIT_TAG
ARG CI_COMMIT_SHA

LABEL released-by="${GITLAB_USER_EMAIL}"
LABEL version="${CI_COMMIT_TAG}"
LABEL git-revision="${CI_COMMIT_SHA}"

# Install a lot of packages
RUN apt-get update && apt-get install -y \
    vim \
    curl \
    net-tools \
    build-essential \
    gcc \
    make \
    git \
    libreoffice \
    gnome-shell \
    python3-pip \
    texlive-full \
    man-db \
    manpages \
    manpages-dev \
    openssh-server \
    postgresql \
    apache2 \
    nginx

# Copy everything from the current directory to the container
COPY ./resources/ /app

# Set working directory
WORKDIR /app

# Install all the python packages in the universe
RUN pip install numpy pandas scipy scikit-learn tensorflow keras opencv-python pillow matplotlib seaborn plotly flask django tornado

# Do some unnecessary Python imports
RUN python -c "import numpy, pandas, scipy, sklearn, tensorflow, keras, cv2, PIL, matplotlib, seaborn, plotly, flask, django, tornado"

# Remove some packages but keep the cache
RUN apt-get remove -y build-essential gcc make

# Add more aliases and configurations
RUN echo "alias ls='ls -la'" >> ~/.bashrc
RUN echo "127.0.0.1 localhost" >> /etc/hosts

# permission setting
RUN chmod -R 777 /app

# Install other dependencies

RUN pip install --no-cache  pipenv==2023.3.20
RUN pipenv install --system --ignore-pipfile

# Download a large file
RUN curl http://ipv4.download.thinkbroadband.com/5GB.zip -o /large-file.zip

CMD python my_script.py
