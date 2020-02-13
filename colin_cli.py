#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os,io,click,requests,time,pint,uuid,barcode,textwrap,urllib
from prettytable import PrettyTable
from pint import UnitRegistry
from PIL import Image,ImageDraw,ImageFont

host = 'colin-uom-dev.herokuapp.com'
port = '80'

hostport = host + ':' + port

ureg = UnitRegistry()


def createLabel(serial_number, fulltext_name, location):
  fnt = ImageFont.truetype('/Library/Fonts/Arial.ttf', 25)

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
      i.show()
  pass

def createChemical():
  click.clear()
  cas = click.prompt('Please enter the CAS number for the new chemical. I will see if we already have some')
  try:
    response = requests.get('http://' + hostport + '/api/chemical/' + cas)
  except:
    click.echo('There seems to be a problem talking to the database...')
    return 0
  if response.status_code == 200:
    chemical = response.json()
    click.echo('Good news! We already have some ' + chemical[0]['prefix'] + chemical[0]['name'])
    cas = chemical[0]['cas']
    prefix = chemical[0].get('prefix','')
    name = chemical[0]['name']
    haz_substance = chemical[0]['haz_substance']
    dg_class = {}
    dg_class[0] = chemical[0].get('dg_class',{}).get('number','')
    dg_class[1] = chemical[0].get('dg_class_2',{}).get('number','')
    dg_class[2] = chemical[0].get('dg_class_3',{}).get('number','')
    packing_group = chemical[0].get('packing_group',{}).get('name','')
    un_number = chemical[0].get('un_number','')
    schedule = chemical[0].get('schedule',{}).get('number','')
  elif response.status_code == 404:
    click.echo("Looks like we don't have any of that. We'll need some more information")
    prefix = click.prompt('What is the prefix of the chemical (if applicable)', default='')
    name = click.prompt('What is the name of the chemical?')
    haz_substance = click.prompt('Is this chemical a hazardous substance? (y/n)')
    dg_class = click.prompt('What is the dangerous goods class of the chemical? Subclasses can be indicated after a comma e.g 3, 6.1', default='').split(', ') + ['','','']
    packing_group = click.prompt('What is the packing group number of the chemical? (I, II, III)', default='')
    un_number = click.prompt('What is the UN number of the chemical?', default='')
    schedule = click.prompt('What is the poisons schedule of this chemical?', default='')


  container_size_string = click.prompt('What is the container size?')
  location = click.prompt('Where will this chemical be stored?')
  supplier = click.prompt('Who is the supplier of this chemical?')
  description = urllib.parse.quote(click.prompt('Any description for this container? (e.g. concentration, solvent, form)', default=''))
  serial_number = click.prompt('The serial number for this container is', default = str(uuid.uuid1().int)[:12])

  container_size = str(ureg(container_size_string).magnitude)
  size_unit = str(ureg(container_size_string).units)

  if click.confirm('Create this chemical?'):
    url = "http://" + hostport + "/api/container/serial/" + str(serial_number) +"?cas=" + str(cas) + "&prefix=" + str(prefix) + "&name=" + str(name) + "&dg_class=" + str(dg_class[0]) + "&dg_class_2=" + str(dg_class[1]) + "&dg_class_3=" + str(dg_class[2]) + "&schedule=" + str(schedule) + "&packing_group=" + str(packing_group) + "&un_number=" + str(un_number) + "&haz_substance=" + str(haz_substance) + "&container_size=" + str(container_size) + "&size_unit=" + str(size_unit) + "&supplier=" + str(supplier) + "&location=" + str(location) + "&supplier=" + str(supplier) + "&description=" + str(description)
    try:
      requests.post(url)
    except:
      click.echo('There seems to be a problem talking to the database. Chemical was not created. HRUMPH.')
      time.sleep(2)
      return 0

    fulltext_name = prefix + name

    labels = [createLabel(serial_number,fulltext_name,location)]
    printLabel(labels)
    click.clear()
  pass

def removeChemical():
  click.clear()
  serial_number = click.prompt('Please enter the serial number of the chemical to be deleted')
  try:
    requests.delete('http://' + hostport + '/api/container/serial/' + serial_number)
    click.echo("Chemical deleted!")
  except:
    click.echo('There seems to be a problem talking to the database...')
  time.sleep(1)
  click.clear()
  pass

def updateLocation():
  click.clear()
  serial_number = click.prompt('Please enter the serial number of the chemical to be updated')
  location = click.prompt('Please enter the new location')
  #location_id = loc[location]
  try:
    requests.put('http://' + hostport + '/api/container/serial/' + serial_number + '?location=' + location + '&temp=false')
  except:
    click.echo('There seems to be a problem talking to the database...')

  #Reprint the label
  try:
    response = requests.get('http://' + hostport + '/api/container/serial/' + serial_number).json()
  except:
    click.echo('There seems to be a problem talking to the database...')
  fulltext_name = response[0]['chemical']['prefix'] + response[0]['chemical']['name']
  location = ' '.join([str(response[0]['storage_location'].get('location', {}).get('parent', {}).get('name', '')), str(response[0]['storage_location'].get('location', {}).get('name', ''))])
  labels = [createLabel(serial_number,fulltext_name,location)]
  printLabel(labels)
  click.echo("Location updated!")
  time.sleep(1)
  click.clear()
  pass

def reprintLabel():
  click.clear()
  serial_number = click.prompt('Enter the serial number of the chemical you wish to reprint the label for')

  try:
    response = requests.get('http://' + hostport + '/api/container/serial/' + serial_number).json()
  except:
    click.echo('There seems to be a problem talking to the database...')

  fulltext_name = response[0]['chemical']['prefix'] + response[0]['chemical']['name']
  location = ' '.join([str(response[0]['storage_location'].get('location', {}).get('parent', {}).get('name', '')), str(response[0]['storage_location'].get('location', {}).get('name', ''))])
  labels = [createLabel(serial_number,fulltext_name,location)]

  printLabel(labels)
  click.clear()
  pass

#This has been deprecated
""" def reprintLabelByLoc():
  click.clear()
  location = click.prompt('Enter the location to print labels for')

  if location in loc:
    location_id = loc[location]
    response = requests.get('http://' + hostport + '/api/container/location_id/' + location_id).json()

    for row in response:
      fulltext_name = row['chemical']['prefix'] + row['chemical']['name']
      location = ' '.join([str(row['container_location'][-1].get('location', {}).get('parent', {}).get('name', '')), str(row['container_location'][-1].get('location', {}).get('name', ''))])
      serial_number = row['serial_number']
      labels = [createLabel(serial_number,fulltext_name,location)]
      printLabel(labels)
    pass
  else:
    click.echo("I didn't recognise that location") """

def setHost():
  click.clear()
  global hostport
  host = click.prompt("Please enter the IP address or hostname of the server")
  hostport = host + ':' + port
  click.clear()

def codeLocation():
  click.clear()
  location = click.prompt('Please enter the full name of the location')
  code = click.prompt('Please enter the shorthand code')
  try:
    requests.put('http://' + hostport + '/api/location/' + location + '?code=' + code )
  except:
    click.echo('There seems to be a problem talking to the database...')
  click.clear()

def stocktake():
  click.clear()
  click.echo("Stocktake mode allows you to specify a location, then scan the chemicals in that location. All chemicals that were previously in that location will be marked as lost.")
  location = click.prompt('Please enter the location to stocktake')
  try:
    response = requests.get('http://' + hostport + '/api/container/location/' + location).json()
  except:
    click.echo("There seems to be a problem talking to the database...")

  for row in response:
    try:
      requests.put('http://' + hostport + '/api/container/serial/' + row['serial_number'] + '?location=Missing&temp=false')
    except:
      click.echo("There seems to be a problem talking to the database...")

  serial_number = ''
  serial_numbers = []
  while serial_number != 'quit':
    serial_number = click.prompt("Enter serial number ('quit' to exit stocktake mode)")

    if (serial_number not in serial_numbers) and (serial_number != 'quit'):
      try:
        response = requests.put('http://' + hostport + '/api/container/serial/' + serial_number + '?location=' + location + '&temp=false').json()
        click.echo(response[0]['chemical']['name_fulltext'])
        serial_numbers.append(serial_number)
      except:
        click.echo("There seems to be a problem talking to the database...")
    else:
      click.echo("Chemical already scanned!")

  '''response = requests.get('http://' + hostport + '/api/container/location/Missing').json()
  t = PrettyTable()
  t.field_names = ["Name"]
  for row in response:
    t.add_row([
    row['chemical']['prefix'] + row['chemical']['name'][0:45]
    ])
  click.echo(t)
  if click.confirm("These chemicals are missing. Delete them?"):
    for row in response:
      requests.delete('http://' + hostport + '/api/container/serial/' + row['serial_number'])
  click.clear()'''
  pass

def locationHistory():
  click.clear()
  serial_number = click.prompt('Please enter the serial number of the chemical')
  try:
    response = requests.get('http://' + hostport + '/api/container/serial/' + serial_number).json()
  except:
    pass
  t = PrettyTable()
  t.field_names = ["Date ", "Location"]
  for row in response[0]['container_location']:
    parent_loc = str(row.get('location', {}).get('parent', {}).get('name', ''))
    cont_loc = str(row.get('location', {}).get('name', ''))
    location = ' '.join([parent_loc, cont_loc])
    t.add_row([
    row['updated_at'],
    location
    ])
  click.echo(t)
  click.prompt("")
  click.clear()

def changeDescription():
  click.clear()
  serial_number = click.prompt('Please enter the serial number of the chemical to be updated')
  description = click.prompt('Please enter the new description', default='')
  try:
    requests.put('http://' + hostport + '/api/container/serial/' + serial_number + '?description=' + description)
  except:
    click.echo('There seems to be a problem talking to the database...')
  click.clear()

@click.command()
def colin():

  ureg = UnitRegistry()
  ureg.define('None = 0')

  while True:
    click.clear()
    click.echo('👨🏻‍🔬 *sighhh* I am CoLIn, what chemical do you want? Enter a name, CAS or container number. CTRL + H for help.')
    click.echo('\nSearch:')
    c = ''
    query = ''
    while query[-1:] != '\r':
      c = click.getchar()
      click.clear()
      if c == '\x7f':
        query = query[:-1]
      elif c == '\x08':
        click.echo('CTRL + N: Create new chemical, CTRL + R: Remove a chemical, CTRL + U: Update location, CTRL + P: Reprint label, CTRL + S: Stocktake, CTRL + O: Add a code for a location, CTRIL + I: View location history, CTRL + T: Connect to a different CoLIn server, CTRL + E: Change a container\'s description')
      elif c == '\x0e':
        createChemical()
      elif c == '\x12':
        removeChemical()
      elif c == '\x15':
        updateLocation()
      elif c == '\x10':
        reprintLabel()
      elif c == '\x14':
        #CTRL T
        setHost()
      elif c == '\x09':
        #CTRL I
        locationHistory()
      elif c == '\x0f':
        #CTRL O
        codeLocation()
      elif c == '\x05':
        #CTRL E
        changeDescription()
      # elif c == '\x0c':
      #   reprintLabelByLoc()
      elif c == '\x13':
        stocktake()
      elif c in ['\x1b[A', '\x1b[B', '\x1b[C', '\x1b[D']:
        pass
      else:
        query = query + c

      click.echo('👨🏻‍🔬 *sighhh* I am CoLIn, what chemical do you want? Enter a name, CAS or container number. CTRL + H for help.')
      click.echo('\nSearch: ' + query)

      if len(query) > 13 and query[-1:] != '\r':
        try:
          response = requests.get('http://' + hostport + '/api/container/search/' + query + '?live=true').json()
          t = PrettyTable()
          t.field_names = ["Name"]
          for row in response:
            t.add_row([
            row['chemical']['prefix'] + row['chemical']['name'][0:45]
            ])
          click.echo(t)
        except:
          pass

      elif query[-1:] == '\r' and len(query) > 2:
        try:
          response = requests.get('http://' + hostport + '/api/container/search/' + query[:-1] + '?live=false').json()
        except:
          click.echo("There seems to be a problem talking to the database...")
        t = PrettyTable()
        t.field_names = ["Serial number", "CAS number", "Name", "DG Class", "Size", "Location", "Supplier"]
        for row in response:
          parent_loc = str(row['current_location'].get('location', {}).get('parent', {}).get('name', ''))
          cont_loc = str(row['current_location'].get('location', {}).get('name', ''))
          location = ' '.join([parent_loc, cont_loc])
          name = row['chemical']['prefix'] + row['chemical']['name'][0:45]
          if row['description']:
           name = name + ' (' + row.get('description', '') + ')'
          t.add_row([
            row['serial_number'],
            row['chemical']['cas'],
            name,
            row['chemical'].get('dg_class', {}).get('description', ''),
            #'{:~}'.format(ureg(str(row['container_size']) + ' ' + str(row['size_unit'])).to_compact()),
            ureg(str(row['container_size']) + ' ' + str(row['size_unit'])),
            location,
            row.get('supplier', {}).get('name', '')
          ])
        click.echo(t)
        click.pause()


if __name__ == '__main__':
    colin()
