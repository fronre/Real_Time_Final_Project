FROM gcc:latest

WORKDIR /app

# Install required packages
RUN apt-get update && apt-get install -y \
    make \
    netcat \
    && rm -rf /var/lib/apt/lists/*

# Copy source files
COPY market_bot.c .
COPY Makefile .

# Build the application
RUN gcc -Wall -Wextra -std=c99 -o market_bot market_bot.c -lpthread

# Expose port
EXPOSE 8080

# Run the application
CMD ["./market_bot"]
