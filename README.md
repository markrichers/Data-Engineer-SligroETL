# 🛒 Project Sligro-Tech Shop

<p align="center">
  <img src="![image](https://github.com/user-attachments/assets/55fcea07-8c3c-4f14-9101-51c23c5da524)" width="200"/>
</p>

---

<p align="center">
  <b>Data-Driven Insights for Smarter Shopping</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Framework-ETL-orange?style=flat-square" alt="ETL Framework">
  <img src="https://img.shields.io/badge/Data-Pandas-blue?style=flat-square" alt="Pandas">
  <img src="https://img.shields.io/badge/Scalable-PySpark-green?style=flat-square" alt="PySpark">
  <img src="https://img.shields.io/badge/License-MIT-blue?style=flat-square" alt="License">
</p>

---

## 🌟 About Sligro-Shop Analytics

**Sligro-Shop Analytics** is a data analysis project designed to process shopping data and calculate insights, including **median values**, using the **Extract, Transform, Load (ETL)** framework.

### Key Features:
- Handles datasets up to **10,000 lines** using **Pandas**.
- Offers scalability for larger datasets through **PySpark** or other distributed data processing tools.
- Provides actionable insights by transforming raw shopping data into meaningful analytics.

### Why Sligro-Tech Shop?
- Small-scale datasets? Use Pandas for quick and efficient processing.
- Growing business? Transition seamlessly to distributed frameworks for big data.

---

## Design Pipeline

![Data Engineer (1)](https://github.com/markrichers/Data-Engineer-SligroETL/assets/50198601/df2a770f-08c0-4c34-b0a9-33b286caef73)


## Setup and Usage

The project is dockerized for ease of setup and ensuring environment consistency across various platforms. Use the following command to build and start the services:
Postgresl will be store direct as the image, and output data processing will load into the microservice database. 


```
docker-compose up -d
```


Once the services are up, you can use Postman or any other API testing tool to test the API endpoints. The project includes a RESTful API built with Flask.

## API Endpoints

The main API endpoint is `http://localhost:5000/metrics/orders`, which can be accessed using the GET method. This endpoint returns calculated median values based on the loaded data.

## Environment Variables

Sensitive and configuration data are stored in the `.env` file. Make sure to populate this file with the correct values before starting the services.
-> it should be on gitignore to keep the embargo level. 

## Project Files

- `data_pipeline.py`: This is the script for the first step of the ETL process following data_engineer.
- `flask_api.py`: This script contains the API endpoint definitions and includes the necessary calculations.

## Development Environment

While this project is OS-independent thanks to Docker, the primary development was done on a Linux machine.

## Contributing

Contributions to this project are welcome. Please ensure that you test your changes thoroughly before submitting a pull request.

## Result with 10000 rows. 

![image](https://github.com/Xccelerated-Assessments/de-assessment-markrichers/assets/50198601/574c842b-ec14-4d41-b73a-67a78da39150)

## Analyze result with 10.000 rows

**"median_session_duration_minutes_before_order": 212.25** - This metric represents the median time a user spends on the site or application before making an order. The median is a type of average that represents the middle value in a list of numbers. In this case, the median time is 212.25 minutes. This means that, on average, users are spending roughly 3.5 hours using the website or application before they decide to make a purchase or order.

**"median_visits_before_order": 2.0** - This is the median number of visits a user makes to the site or application before they make an order. A visit often refers to a session, or a period of time during which a user is actively engaged with a website. In this case, the median is 2.0, suggesting that, on average, users visit the site or app twice before making a purchase or order.

## Analyze result with all rows:

```json line
{
    "median_session_duration_minutes_before_order": 3260.625,
    "median_visits_before_order": 28.0
}
```

***"median_session_duration_minutes_before_order": 3260.625***: This is the median duration of user sessions in minutes before an order is made. This means that in a sorted list of all session durations (from shortest to longest) leading up to an order, the middle value is 3260.625 minutes. It suggests that users typically spend this much time on the platform across multiple sessions before making an order.

***"median_visits_before_order": 28.0***: This is the median number of user visits to the platform before an order is made. This means that in a sorted list of all visit counts leading up to an order, the middle value is 28. This suggests that users typically visit the platform this many times before making an order.

Note that both of these values are medians, not averages (means). The median is the middle value in a sorted list, and it is a type of measure of central tendency that can be more representative than the average in datasets with extreme values or skewness.


## Suggestion other method
- Pyspark - Distributed Processing Databrick
- Multithreading
- Incremental loading ( download as txt and then process )

Current process for total data with normal pandas is; Total processing time: **41.0708483616511 minutes**
Total rows in the 'events' table: 185114



