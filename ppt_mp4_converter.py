#!/usr/bin/env python3

import sys
import bs4
import tempfile
import argparse
import pdf2image
import subprocess

from pathlib import Path
from zipfile import ZipFile


class AppArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(description='Convert ppt to mp4', *args, **kwargs)
        self.add_argument('--ppt', required=True, help='Path to ppt file')
        self.add_argument('--pdf', required=True, help='Path to pdf file')
        self.add_argument('output', help='Output mp4 file')
    

class PptAudioExtract:
    def __init__(self, ppt_path):
        self.ppt_path = ppt_path

    def extract(self, extract_directory):
        with ZipFile(str(self.ppt_path), 'r') as zip_file:
            zip_file.extractall(extract_directory)

        slides_audio = {}
        
        slides_directory = Path(extract_directory) / 'ppt' / 'slides' / '_rels'
        for slide_file in slides_directory.iterdir():
            index = (self.__extract_slide_id_from_filename(slide_file.name))
            with slide_file.open() as f:
                data = bs4.BeautifulSoup(f.read(), 'lxml')
                for relationship in data.html.body.relationships:
                    if isinstance(relationship, bs4.element.Tag):
                        target_file = relationship['target']
                        if target_file.endswith('wav'):
                            slides_audio[index] = (slides_directory.parent / target_file).resolve()
                            break

        return slides_audio

    def __extract_slide_id_from_filename(self, slide_filename):
        # Format: slideXX.xml.rels
        return int(slide_filename.split('.')[0][5:])


class PptToMp4Converter:
    def __init__(self, ppt_path, pdf_path, output_path):
        self.ppt_path = ppt_path
        self.pdf_path = pdf_path
        self.output_path = output_path

    def run(self):
        with tempfile.TemporaryDirectory() as temp_path:
            print(temp_path)
            input()

            slides_path = Path(temp_path)

            slides = pdf2image.convert_from_path(self.pdf_path)
            slides_audio = PptAudioExtract(self.ppt_path).extract(temp_path)

            ts_files = []
            
            for index, slide_image in enumerate(slides, 1):
                try:
                    print('Generowanie klatki', index)

                    slide_mp4_path = str(slides_path / f'{index}.mp4')
                    slide_ts_path = str(slides_path / f'{index}.ts')
                    slide_image_path = str(slides_path / f'{index}.jpg')
                    slide_audio_path = slides_audio[index] if index in slides_audio else None
                    ts_files.append(slide_ts_path)
                    
                    if Path(slide_ts_path).exists():
                        continue

                    slide_image.save(slide_image_path)
                
                    if slide_audio_path is None:
                        self.__create_slide_video_without_audio(slide_image_path, slide_mp4_path)
                    else:
                        self.__create_slide_video_with_audio(slide_image_path, slide_audio_path, slide_mp4_path)

                    self.__create_ts_file(slide_mp4_path, slide_ts_path)    
                except Exception as e:
                    print(f'NIE UDAŁO SIĘ WYGENEROWAĆ KLATKI {index}!')
                    print(e)

            self.__concatenate_videos(ts_files, self.output_path)

    def __create_slide_video_without_audio(self, slide_image_path, slide_mp4_path):
        subprocess.call(['ffmpeg', '-loop', '1', '-i', slide_image_path, '-c:v', 'libx264',
                '-t', '10', '-pix_fmt', 'yuv420p', '-shortest', slide_mp4_path])

    def __create_slide_video_with_audio(self, slide_image_path, slide_audio_path, slide_mp4_path):
        subprocess.call(['ffmpeg', '-loop', '1', '-y', '-i', slide_image_path, '-i', slide_audio_path,
              '-c:v', 'libx264', '-tune', 'stillimage', '-c:a', 'aac',
              '-b:a', '192k', '-pix_fmt', 'yuv420p', '-shortest', slide_mp4_path])

    def __create_ts_file(self, slide_mp4_path, slide_ts_path):
        subprocess.call(['ffmpeg', '-y', '-i', slide_mp4_path, '-c', 'copy',
              '-bsf:v', 'h264_mp4toannexb', '-f', 'mpegts', slide_ts_path])

    def __concatenate_videos(self, ts_files, out_path):
        command = 'concat:' + '|'.join(ts_files)
        subprocess.call(['ffmpeg', '-y', '-f', 'mpegts', '-i', command,
            '-c', 'copy', '-bsf:a', 'aac_adtstoasc', out_path])


def main():
    args = AppArgumentParser().parse_args()
    PptToMp4Converter(args.ppt, args.pdf, args.output).run()


if __name__ == '__main__':
    main()
