FROM python:3.11-slim

# Install dependencies
RUN pip install --no-cache-dir verdictos-scan requests

# Set working directory
WORKDIR /code

# Default command
ENTRYPOINT ["verdictos-scan"]
CMD ["--help"]

# Usage:
# docker run -v $(pwd):/code verdictos/scan --path /code
