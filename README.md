# specimen-app
simple Specimen app



## Getting Started

### Prerequisites
- Docker

### Installation

1. Clone the repo
```sh
$ git clone https://github.com/yijia1127cs06g/specimen-app.git
```
2. Start Specimen app
```sh
$ docker-compose -f docker-compose.yml up
```
3. Load specimen fixture
```sh
$ docker exec specimen-api-server python load_specimen_fixtures.py
```

## Usage
- After starting Specimen app, you can see [http://localhost:8000](http://localhost:8000) show below message.
    ```json
    {
      "message": "Hi~ This is Specimen App for specimen"
    }
    ```
- Other usage see [Api Documentation](http://localhost:8000/docs)
