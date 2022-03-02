#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os,io,click,requests,time,textwrap,urllib,barcode
from PIL import Image,ImageDraw,ImageFont

url = 'https://colin-uom.herokuapp.com'
#url = 'http://localhost:9292'

headers = {'User-Agent': 'Mozilla/5.0'}
payload = {'username':'cli','password':'cli'}
#payload = {'username':'root','password':'root'}

session = requests.Session()


def createLabel(serial_number, fulltext_name, location):
  fnt = ImageFont.truetype('arial.ttf', 25)

  code128 = barcode.get('code128', serial_number, writer = barcode.writer.ImageWriter())
  barcode_image = code128.render().resize((300,120)).crop((0,0,300,80))

  label = Image.new('1', (696,120), color=1)
  label.paste(barcode_image, box=(0,0))

  lines = textwrap.wrap(fulltext_name[:75], width = 25)
  y_text=5

  text = ImageDraw.Draw(label)

  for line in lines:
    width, height = fnt.getsize(line)
    text.text((320, y_text), line, font=fnt, fill=0)
    y_text += height

  text.text((65,93), serial_number, font=fnt, fill=0)
  text.text((320,95), location, font=fnt, fill=0)
  text.text((660,10), "J", font=fnt, fill=0)
  text.text((660,45), "M", font=fnt, fill=0)
  text.text((660,80), "W", font=fnt, fill=0)

  return label

def createTextLabel(name):
  fnt = ImageFont.truetype('arial.ttf', 120)

  label = Image.new('1', (696,120), color=1)

  text = ImageDraw.Draw(label)

  text.text((0,0), name, font=fnt, fill=0)

  return label

def printLabel(image):
  from brother_ql.raster import BrotherQLRaster
  from brother_ql.conversion import convert
  from brother_ql.backends.helpers import send

  send_to_printer = True

  if send_to_printer:
    backend = 'pyusb'
    model = 'QL-570'
    printer = 'usb://0x04f9:0x2028/C7Z863490'

    qlr = BrotherQLRaster(model)
    convert(qlr, image, '62')
    try:
      send(instructions = qlr.data, printer_identifier = printer, backend_identifier = backend, blocking=True)
    except:
      click.echo("Printer not connected")
      time.sleep(2)
  else:
    for i in image:
      i.save('test.png')
  pass

def reprintLabel():
  click.clear()
  serial_number = click.prompt('Enter the barcode of the chemical you wish to reprint the label for')
  session.post(url + '/user/login',headers=headers,data=payload)

  response = session.get(url + '/api/container/barcode/' + serial_number, headers=headers, data=payload).json()

  fulltext_name = response[0]['chemical']['prefix'] + response[0]['chemical']['name']
  location = str(response[0]['current_location'].get('location', {}).get('parent', {}).get('name', {})) + ' ' + str(response[0]['current_location'].get('location', {}).get('name', {}))
  labels = [createLabel(serial_number,fulltext_name,location)]

  printLabel(labels)


  
  pass

@click.command()
def colin():
  while True:
    reprintLabel()

if __name__ == '__main__':
    colin()
