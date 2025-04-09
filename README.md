# image_parser
## info
The parser collects images from open sources currently supported by istockphoto, google images, unsplash. Switching between them happens automatically. The parser supports collecting 10,000+ images in a single request.
## using
```sh
python main.py --query people --limit 1000 --browser edge --output_dir people
```
- **query** - query (word or phrase)
- **limit** - requied number of images
- **browser** - the browser that will be used by the program (must be in the system), google chrome, edge, firefox are supported
- **output_dir** - the directory where the images will be saved (default: images)
## Usage Instructions

To use this project with Freepik.com, you need to obtain an API key from Freepik. Once you have the API key, add it to a `.env` file in the root directory of the project. The key should be added in the following format:
```sh
FREEPIK_API_KEY=your_api_key_here
```
Make sure that the `.env` file is included in your `.gitignore` to avoid accidentally exposing your API key to the public. This project relies on the Freepik API to fetch resources, and without a valid API key, the functionality will not work as intended.
## versions
1.0 -- It supports 3 browsers and 3 websites with images. Certificate errors may occur for individual images, but this does not affect the parser.
---

## Disclaimer

The creator of this project is not responsible for any unauthorized or illegal use of the parser. This tool is designed for educational and legitimate purposes only. If the code is used in a manner that violates copyright laws or Freepik's terms of service, the responsibility lies solely with the user. Always ensure that your usage complies with the relevant legal and licensing requirements. Misuse of this project may result in legal consequences, and the project maintainer disclaims any liability for such actions.
