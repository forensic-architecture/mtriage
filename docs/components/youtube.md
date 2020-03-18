# Configuring the Youtube selector 

In order to run the Youtube selector, mtriage requires a Google Cloud Platform
API key.

1. Create a new project in GCP, and in the [credentials
   page](https://console.cloud.google.com/apis/credentials), enable the
   'Youtube Data V3' API.
2. Create a new API key, ensuring that it has access to the Youtube V3 API. 
3. In the '.env' file in mtriage's root folder, add the line
   `GOOGLE_API_KEY=xxxxx`, replacing 'xxxxx' with your downloaded API key. 
