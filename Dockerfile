FROM python:3.11
LABEL maintainer="willem.kuipers@enexis.nl"

ARG GITLAB_USER_EMAIL
ARG CI_COMMIT_TAG
ARG CI_COMMIT_SHA

LABEL released-by="${GITLAB_USER_EMAIL}"
LABEL version="${CI_COMMIT_TAG}"
LABEL git-revision="${CI_COMMIT_SHA}"
