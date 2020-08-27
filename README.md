# ppt_mp4_converter

Script, which converts *ppt* files to *mp4*. It takes on board narration audio files, associated with slides.

## Installation

```bash
$ git clone https://github.com/qwercik/ppt_mp4_converter
$ cd ppt_mp4_converter
$ pip install -r requirements.txt
```

## Usage

First, generate PDF file from PPT, using a dedicated PPT files reader (MS Powerpoint, Libre Office Impress *etc.*). Make sure, the presentation have no hidden slides, and PDF have the same number of pages, as the PPT.

Next, run the following command

```
$ ./ppt_mp4_converter --ppt <ppt_file> --pdf <pdf_file> <output_file>
```

Where:

- `<ppt_file>` - path to ppt/pptx presentation file
- `<pdf_file>` - path to pdf file, exported from presentation
- `<output_file>` - path to output mp4 file

## Acknowledgements

Thanks to [chaonan99](https://github.com/chaonan99), who was an author of the [original version of script](https://github.com/chaonan99/ppt_presenter), on which I based this project.