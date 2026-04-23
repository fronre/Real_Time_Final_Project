#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/time.h>
#include <pthread.h>

#define PORT 8080
#define BUFFER_SIZE 1024
#define NUM_ASSETS 10
#define MAX_TASKS 100

typedef struct {
    char symbol[16];
    double price;
    double balance;
    double volume;
    long timestamp_sec;
    long timestamp_usec;
    double volatility;
    double trend;
} MarketData;

typedef enum {
    BUY,
    SELL
} OrderType;

typedef struct {
    int id;
    OrderType type;
    char symbol[16];
    double price;
    int quantity;
    long deadline_sec;
    long deadline_usec;
    long created_sec;
    long created_usec;
    int priority;
    int executed;
    long executed_sec;
    long executed_usec;
    int missed_deadline;
} TradingTask;

typedef struct {
    char symbol[16];
    double base_price;
    double current_price;
    double volatility;
    double trend_strength;
    int trading_speed;
} DigitalAsset;

DigitalAsset assets[NUM_ASSETS] = {
    {"BTC", 45000.0, 45000.0, 0.08, 0.6, 1},
    {"ETH", 3000.0, 3000.0, 0.10, 0.5, 1},
    {"USDT", 1.0, 1.0, 0.01, 0.1, 3},
    {"PUBG_UC", 0.01, 0.01, 0.15, 0.7, 2},
    {"COD_POINTS", 0.02, 0.02, 0.12, 0.6, 2},
    {"NETFLIX", 15.0, 15.0, 0.05, 0.3, 3},
    {"SPOTIFY", 10.0, 10.0, 0.04, 0.2, 3},
    {"VPN_PREMIUM", 5.0, 5.0, 0.03, 0.1, 3},
    {"DOMAIN_COM", 25.0, 25.0, 0.06, 0.4, 2},
    {"NFT_ART", 100.0, 100.0, 0.20, 0.8, 1}
};

TradingTask task_queue[MAX_TASKS];
int task_count = 0;
int next_task_id = 1;
pthread_mutex_t task_mutex = PTHREAD_MUTEX_INITIALIZER;

long get_microseconds() {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return tv.tv_sec * 1000000 + tv.tv_usec;
}

void get_current_time(long *sec, long *usec) {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    *sec = tv.tv_sec;
    *usec = tv.tv_usec;
}

void generate_trading_tasks() {
    pthread_mutex_lock(&task_mutex);
    
    for (int i = 0; i < NUM_ASSETS && task_count < MAX_TASKS; i++) {
        if ((rand() % 100) < 20) {
            TradingTask task;
            task.id = next_task_id++;
            task.type = (rand() % 2) ? BUY : SELL;
            strcpy(task.symbol, assets[i].symbol);
            task.price = assets[i].current_price;
            task.quantity = (rand() % 100) + 1;
            
            long current_sec, current_usec;
            get_current_time(&current_sec, &current_usec);
            
            task.created_sec = current_sec;
            task.created_usec = current_usec;
            
            long deadline_offset = (rand() % 5000000) + 100000;
            task.deadline_sec = current_sec;
            task.deadline_usec = current_usec + deadline_offset;
            
            if (task.deadline_usec >= 1000000) {
                task.deadline_sec += task.deadline_usec / 1000000;
                task.deadline_usec %= 1000000;
            }
            
            task.priority = 1000000 - deadline_offset;
            
            task_queue[task_count++] = task;
        }
    }
    
    pthread_mutex_unlock(&task_mutex);
}

int compare_tasks(const void *a, const void *b) {
    const TradingTask *task_a = (const TradingTask *)a;
    const TradingTask *task_b = (const TradingTask *)b;
    
    if (task_a->deadline_sec != task_b->deadline_sec) {
        return task_a->deadline_sec - task_b->deadline_sec;
    }
    return task_a->deadline_usec - task_b->deadline_usec;
}

void execute_next_task() {
    pthread_mutex_lock(&task_mutex);
    
    if (task_count == 0) {
        pthread_mutex_unlock(&task_mutex);
        return;
    }
    
    // Sort by EDF
    qsort(task_queue, task_count, sizeof(TradingTask), compare_tasks);
    
    TradingTask *task = &task_queue[0];
    long current_sec, current_usec;
    get_current_time(&current_sec, &current_usec);
    
    // Check if deadline missed
    if (current_sec > task->deadline_sec || 
        (current_sec == task->deadline_sec && current_usec >= task->deadline_usec)) {
        task->missed_deadline = 1;
        printf("🚨 MISSED DEADLINE: Task #%d - %s %s (Deadline: %ld.%06ld)\n", 
               task->id, task->symbol, task->type == BUY ? "BUY" : "SELL",
               task->deadline_sec, task->deadline_usec);
        
        // Remove missed task
        for (int i = 0; i < task_count - 1; i++) {
            task_queue[i] = task_queue[i + 1];
        }
        task_count--;
    } else {
        // Execute task
        task->executed = 1;
        task->executed_sec = current_sec;
        task->executed_usec = current_usec;
        
        printf("✅ EXECUTED: [%ld.%06ld] Task #%d - %s %d %s at $%.6f (Deadline: %ld.%06ld)\n", 
               current_sec, current_usec, task->id, 
               task->type == BUY ? "BUY" : "SELL", task->quantity, task->symbol, task->price,
               task->deadline_sec, task->deadline_usec);
        
        // Remove executed task
        for (int i = 0; i < task_count - 1; i++) {
            task_queue[i] = task_queue[i + 1];
        }
        task_count--;
    }
    
    pthread_mutex_unlock(&task_mutex);
}

void schedule_tasks_edf() {
    pthread_mutex_lock(&task_mutex);
    
    qsort(task_queue, task_count, sizeof(TradingTask), compare_tasks);
    
    pthread_mutex_unlock(&task_mutex);
}

void generate_market_data(MarketData *data) {
    static int asset_index = 0;
    
    asset_index = (asset_index + 1) % NUM_ASSETS;
    DigitalAsset *asset = &assets[asset_index];
    
    double volatility_factor = asset->volatility;
    double trend_factor = asset->trend_strength;
    
    double random_change = (rand() % 200 - 100) / 100.0;
    double trend_change = (rand() % 100) / 100.0 * trend_factor;
    
    asset->current_price += (random_change * volatility_factor + trend_change);
    
    if (asset->current_price < asset->base_price * 0.5) {
        asset->current_price = asset->base_price * 0.5;
    }
    if (asset->current_price > asset->base_price * 2.0) {
        asset->current_price = asset->base_price * 2.0;
    }
    
    strcpy(data->symbol, asset->symbol);
    data->price = asset->current_price;
    data->balance = 10000.0 + (rand() % 5000);
    data->volume = (rand() % 10000) + 1000;
    data->volatility = asset->volatility;
    data->trend = asset->trend_strength;
    
    get_current_time(&data->timestamp_sec, &data->timestamp_usec);
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
    
    printf("🤖 Enhanced Market Bot with EDF Scheduling listening on port %d...\n", PORT);
    printf("📈 Supporting %d digital assets with microsecond timing...\n", NUM_ASSETS);
    printf("⏱️  EDF Task Scheduling Algorithm Active...\n");
    printf("Waiting for Python server to connect...\n");
    
    pthread_mutex_init(&task_mutex, NULL);
    
    // Accept connection
    if ((new_socket = accept(server_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen)) < 0) {
        perror("accept");
        exit(EXIT_FAILURE);
    }
    
    printf("✅ Connected to Python server!\n");
    printf("📈 Starting real-time digital asset trading simulation...\n");
    printf("⚡ High-frequency trading with microsecond precision enabled...\n\n");
    
    srand(time(NULL));
    
    int counter = 0;
    while (1) {
        counter++;
        
        if (counter % 3 == 0) {
            generate_trading_tasks();
            schedule_tasks_edf();
        }
        
        if (counter % 2 == 0) {
            execute_next_task();
        }
        
        generate_market_data(&market_data);
        
        snprintf(buffer, BUFFER_SIZE, "%s:%.6f:%.2f:%.0f:%ld:%ld:%.3f:%.3f\n",
                 market_data.symbol,
                 market_data.price,
                 market_data.balance,
                 market_data.volume,
                 market_data.timestamp_sec,
                 market_data.timestamp_usec,
                 market_data.volatility,
                 market_data.trend);
        
        if (send(new_socket, buffer, strlen(buffer), 0) < 0) {
            perror("send failed");
            break;
        }
        
        printf("📊 Sent: %s", buffer);
        
        if (counter % 10 == 0 && task_count > 0) {
            pthread_mutex_lock(&task_mutex);
            printf("🔄 EDF Queue: %d active tasks\n", task_count);
            if (task_count > 0) {
                printf("⏰ Next deadline: %ld.%06ld (Task #%d - %s %s)\n", 
                       task_queue[0].deadline_sec, task_queue[0].deadline_usec,
                       task_queue[0].id, task_queue[0].symbol,
                       task_queue[0].type == BUY ? "BUY" : "SELL");
            }
            pthread_mutex_unlock(&task_mutex);
        }
        
        usleep(50000);  // 50ms for faster real-time processing
    }
    
    pthread_mutex_destroy(&task_mutex);
    close(new_socket);
    close(server_fd);
    return 0;
}
