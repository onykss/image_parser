# image_parser
## info
The parser collects images from open sources currently supported by istockphoto, google images, unsplash. Switching between them happens automatically. The parser supports collecting 10,000+ images in a single request.
## using
```sh
python main.py --query people --limit 1000 --browser edge --output_dir people
```
- **query** - query (word or phrase)\
- **limit** - requied number of images\
- **browser** - the browser that will be used by the program (must be in the system), google chrome, edge, firefox are supported\
- **output_dir** - the directory where the images will be saved (default - images)\
## versions
1.0 -- It supports 3 browsers and 3 websites with images. Certificate errors may occur for individual images, but this does not affect the parser.
