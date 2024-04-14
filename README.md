# specimen-app
simple Specimen app


## 1. Getting Started

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
$ docker exec specimen-api-server python load_initial_fixtures.py
```

## 2. Usage
- After starting Specimen app, you can see [http://localhost:8000](http://localhost:8000) show below message.
    ```json
    {
      "message": "Hi~ This is Specimen App for specimen"
    }
    ```
- Other usage see [Api Documentation](http://localhost:8000/docs)

## 3. Crawl Specimen from sinica
1. Run specimen-api-server container interactively.
```sh
$ docker run -it specimen-api-server bash
```
2. After entered specimen-api-server shell, 
   1. First, crawl the list of sinica ids. You can specify the needed page
      ```sh
      $ python crawl_specimen_lists.py
      
      # Specify the start page and end page. Default is 1 and 100.
      $ python crawl_specimen_lists.py --start-page 200 --end-page 300
      
      # Set Concurrency. Default is 3
      $ python crawl_specimen_lists.py --concurrency 4
      ```
   2. Then, run the crawl_specimens.py to crawl the unfinished specimens.
      ```sh
      $ python crawl_specimens.py
      
      # Specify the limit and Concurrency. Default is 100 and 3.
      $ python crawl_specimens.py --limit 1000 --concurrency 4
      ```
   3. (Optional) Both script can run test mode. Test mode will emulate crawling the response from `example_html` and `example_page`
      ```sh
      $ python crawl_specimen_lists.py --start-page 1 --end-page 3 --test-mode True
      $ python crawl_specimens.py --test-mode True
      ```

## 4. Task list
- [X] crawl data from [sinica](https://sinica.digitalarchives.tw/collection.php?type=3799)（only 臺灣本土植物數位化典藏）
- [X] create a simple restful application with an endpoint to query the crawled specimens.
  - [X] can written in node.js(Nest.js), *python(fast api)* or golang(gin)
  - [X] use swagger ui to document the api
  - [X] [bonus] create an endpoint to download the crawled data including image as a PDF.
- [X] please use git to manage code and commit to github.
  - [X] for reproducibility, please write a README.md to describe how to start the crawler and application.
  - [X] [bonus] use docker to containerize the application

## 5. Others
- Be careful to download specimen pdf by [/specimens/1/download](http://localhost:8000/specimens/1/download). It will make a request to sinica. Sinica website experiences noticeable performance issues at night may due to limited server resources(Even unavailable to access).
