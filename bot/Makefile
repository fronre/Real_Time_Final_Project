CC = gcc
CFLAGS = -Wall -Wextra -std=c99
TARGET = market_bot
SOURCE = market_bot.c
LIBS = -lpthread

all: $(TARGET)

$(TARGET): $(SOURCE)
	$(CC) $(CFLAGS) -o $(TARGET) $(SOURCE) $(LIBS)

clean:
	rm -f $(TARGET)

.PHONY: all clean
