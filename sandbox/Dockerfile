# Static-analysis sandbox for cloned paper repositories (M7, Phase 4).
# Repo code is NEVER executed: the container only reads files with git, ast and yaml.
# Run with: docker run --rm --network none --read-only --memory 512m --pids-limit 64 \
#   -v <clone>:/repo:ro paperlens-sandbox <analysis command>
FROM python:3.11-slim
RUN pip install --no-cache-dir pyyaml==6.0.2 tomli==2.0.2 \
    && useradd --create-home --uid 10001 analyzer
USER analyzer
WORKDIR /work
ENTRYPOINT ["python", "-I"]
