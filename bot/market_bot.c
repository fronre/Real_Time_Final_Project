#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define PORT 8080
#define BUFFER_SIZE 1024

typedef struct {
    double price;
    double balance;
    double volume;
    char symbol[16];
    long timestamp;
} MarketData;

void generate_market_data(MarketData *data) {
    static double base_price = 100.0;
    static double base_balance = 10000.0;
    
    // Simulate price fluctuation
    double change = (rand() % 200 - 100) / 100.0; // -1.0 to 1.0
    base_price += change;
    if (base_price < 50.0) base_price = 50.0;
    if (base_price > 200.0) base_price = 200.0;
    
    // Simulate balance changes
    base_balance += (rand() % 1000 - 500) / 10.0;
    
    data->price = base_price;
    data->balance = base_balance;
    data->volume = rand() % 10000 + 1000;
    strcpy(data->symbol, "AAPL");
    data->timestamp = time(NULL);
}

int main() {
    int server_fd, new_socket;
    struct sockaddr_in address;
    int opt = 1;
    int addrlen = sizeof(address);
    char buffer[BUFFER_SIZE] = {0};
    MarketData market_data;
    
    // Create socket file descriptor
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }
    
    // Set socket options
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt))) {
        perror("setsockopt");
        exit(EXIT_FAILURE);
    }
    
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);
    
    // Bind socket to port
    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        perror("bind failed");
        exit(EXIT_FAILURE);
    }
    
    // Listen for connections
    if (listen(server_fd, 3) < 0) {
        perror("listen");
        exit(EXIT_FAILURE);
    }
    
    printf("🤖 Market Bot listening on port %d...\n", PORT);
    printf("Waiting for Python server to connect...\n");
    
    // Accept connection
    if ((new_socket = accept(server_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen)) < 0) {
        perror("accept");
        exit(EXIT_FAILURE);
    }
    
    printf("✅ Connected to Python server!\n");
    printf("📈 Starting real-time market data generation...\n\n");
    
    // Seed random number generator
    srand(time(NULL));
    
    // Generate and send market data continuously
    while (1) {
        generate_market_data(&market_data);
        
        // Format data as a simple string: "symbol:price:balance:volume:timestamp"
        snprintf(buffer, BUFFER_SIZE, "%s:%.2f:%.2f:%.0f:%ld\n",
                 market_data.symbol,
                 market_data.price,
                 market_data.balance,
                 market_data.volume,
                 market_data.timestamp);
        
        // Send data to Python server
        if (send(new_socket, buffer, strlen(buffer), 0) < 0) {
            perror("send failed");
            break;
        }
        
        printf("📊 Sent: %s", buffer);
        
        // Sleep for 1 second before next update
        sleep(1);
    }
    
    close(new_socket);
    close(server_fd);
    return 0;
}
