FROM gcc:latest
WORKDIR /app
COPY . .
RUN gcc -Wall -Wextra -std=c99 -o market_bot market_bot.c -lpthread
CMD ["./market_bot"]
