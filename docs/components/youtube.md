# Selector: `youtube`

In order to run the youtube selector, mtriage requires a Google Cloud Platform service account.

1. Create a service account and download a 'credentials.json' from the credentials page](https://console.cloud.google.com/apis/credentials) in the Google Cloud console.
2. Move the downloaded JSON file to credentials/google.json. This file is
   gitignored, and so will not be pushed to any remotes.
3. In the service account API settings on Google Cloud Console in the browser, enable the "Youtube Data v3 API".
