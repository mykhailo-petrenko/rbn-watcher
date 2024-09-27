# RBN Watcher

## Scope 
- As a radio amateur I want to be notified when another radio amateur with desired callsign appears on air.

## Architecture

![Architecture](docs/FindHamMate.drawio.png)

- Let's use RabbitMQ pub/sub as message broker to connect RBN with subscribers.
- RBN consumer, who sent all spots to broker written on python.
- Telegram bot will be on python in sake of simplicity.
- Subscriptions state could be stored in mysql-lite

## Start 

### Broker
```shell
docker compose up
```

### Emiter
```shell
source venv/bin/activate
python emit_log_direct.py
```

### Receiver
```shell
source venv/bin/activate
python receive_logs_direct.py
```

## Setup ENV
```shell
python -m venv 
```

