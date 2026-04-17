CC = gcc
CFLAGS = -Wall -Wextra -std=c99
TARGET = market_bot
SOURCE = market_bot.c

all: $(TARGET)

$(TARGET): $(SOURCE)
	$(CC) $(CFLAGS) -o $(TARGET) $(SOURCE)

clean:
	rm -f $(TARGET)

.PHONY: all clean
