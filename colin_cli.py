#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os,io,click,requests,time,pint,uuid,barcode,textwrap
from prettytable import PrettyTable
from pint import UnitRegistry
from PIL import Image,ImageDraw,ImageFont

host = 'localhost'
port = '9292'

hostport = host + ':' + port

ureg = UnitRegistry()

pg = {
  "I": "1",
  "II": "2",
  "III": "3",
  "-": "",
  "": ""
}

sched = {
  "1": "",
  "2": "2",
  "4": "3",
  "6": "6",
  "7": "7",
  "-": "",
  "": ""
}

dg = {
  "2.1": "9",
  "3": "12",
  "4.1": "14",
  "4.2": "15",
  "4.3": "16",
  "5.1": "18",
  "5.2": "19",
  "6": "20",
  "6.1": "21",
  "8": "24",
  "9": "25",
  "-": "",
  "": ""
}

loc = {
  "Harmful H1": "2",
  "Harmful H2": "3",
  "Harmful H3": "4",
  "Harmful H4": "5",
  "Harmful H5": "6",
  "Harmful H6": "7",
  "Harmful H7": "8",
  "Harmful H8": "9",
  "Harmful H9": "10",
  "Harmful H10": "11",
  "Harmful H11": "12",
  "Harmful H12": "13",
  "Harmful H13": "14",
  "Harmful H14": "15",
  "Harmful H15": "16",
  "Harmful H16": "17",
  "Harmful H17": "18",
  "Harmful H18": "19",
  "Harmful H19": "20",
  "Harmful H20": "21",
  "Harmful H21": "22",
  "Harmful H22": "23",
  "Harmful H23": "24",
  "Harmful H24": "25",
  "Harmful H25": "26",
  "Harmful H26": "27",
  "Harmful H27": "28",
  "Harmful Desc": "29",
  "Toxic TS1": "31",
  "Toxic TS2": "32",
  "Toxic TS3": "33",
  "Toxic TM1": "34",
  "Toxic TM2": "35",
  "Toxic TM3": "36",
  "Toxic TM4": "37",
  "Toxic TM5": "38",
  "Toxic TM6": "39",
  "Toxic TL1": "40",
  "Toxic TL2": "41",
  "Toxics TL2": "41",
  "Toxic TL3": "42",
  "Toxic TL4": "43",
  "Toxic TXL": "44",
  "Toxic dessicator": "45",
  "Corrosive 1": "47",
  "Corrosive 2": "48",
  "Corrosive Acid 1": "47",
  "Corrosive Acid 2": "48",
  "Corrosive acid 1": "47",
  "Corrosive acid 2": "48",
  "Corrosive Basic 1": "49",
  "Corrosive Basic 2": "50",
  "Corrosive Basic 3": "51",
  "Corrosive Basic 4": "52",
  "Corrosive basic 1": "49",
  "Corrosive basic 2": "50",
  "Corrosive basic 3": "51",
  "Corrosive basic 4": "52",
  "Corrosive Desc": "53",
  "Fridge Bottom draw": "55",
  "Fridge (bottom)": "55",
  "Fridge door": "56",
  "Fridge Door": "56",
  "Fridge 3 Door": "56",
  "Fridge S1": "57",
  "Fridge S1 B1": "58",
  "Fridge S1 B3": "59",
  "Fridge S2 B1": "60",
  "Fridge S2 B2": "61",
  "Fridge S3": "62",
  "Fridge S3 B1": "63",
  "Fridge S4": "64",
  "Fridge S4 B1": "65",
  "Freezer 1 S1": "67",
  "Freezer 1 S1 B1": "68",
  "Freezer 1 S1B1": "68",
  "Oxidant Freezer": "68",
  "Freezer 1 S2 B1": "69",
  "Freezer 1 S2 B2": "70",
  "Freezer 1 S2 B3": "71",
  "Freezer 1 S3 B1": "72",
  "Freezer 1 S4 B1": "73",
  "Freezer 1 S4 B2": "74",
  "Freezer 1 S5 B1": "75",
  "Freezer 2 (Corrosive)": "76",
  "Middle freezer": "76",
  "Freezer 3 (Flammable)": "77",
  "Flammable liquids L": "79",
  "Flammable liquids S": "80",
  "Flammable Liquids L": "79",
  "Flammable Liquids S": "80",
  "Flammable liquid L": "79",
  "Flammable liquid S": "80",
  "Flammable Liquid L": "79",
  "Flammable Liquid S": "80",
  "Flammable Solids": "81",
  "Flammable Solids Desc 1": "82",
  "Flammable Solids Desc 2": "83",
  "Flammable Solid": "81",
  "Flammable Solid Desc 1": "82",
  "Flammable Solid Desc 2": "83",
  "Poison Draw No. 1": "85",
  "Poisons draw No.1": "85",
  "Poisons draw No.2": "86",
  "Poisons draw No.3": "87",
  "Poisons draw no.3": "87",
  "Bench 1": "89",
  "Bench 2": "90",
  "Bench 3": "91",
  "Bench 4": "92",
  "Bench 5": "93",
  "Bench 6": "94",
  "Bench 7": "95",
  "Bench 8": "96",
  "Bench 9": "97",
  "Bench 10": "98",
  "Bench 11": "99",
  "Bench 12": "100",
  "Bench 13": "101",
  "Bench 14": "102",
  "Bench 14 desc": "102",
  "Dangerous When Wet": "103",
  "Oxidizing agents": "104",
  "Oxidants": "104",
  "Non-hazardous": "105",
  "Under Sinks": "105",
  "various": "105",
  "Non-Flammable Solvents": "109",
  "Chromatog/filtration aids": "106",
  "Deuterates desc": "107",
  "Sieves/drying agents": "108",
}

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
  else:
    for i in image:
      i.show()
  pass

def createChemical():
  click.clear()
  cas = click.prompt('Please enter the CAS number for the new chemical. I will see if we already have some')
  response = requests.get('http://' + hostport + '/api/chemical/' + cas)
  if response.status_code == 200:
    chemical = response.json()
    click.echo('Good news! We already have some ' + chemical[0]['prefix'] + chemical[0]['name'])
    cas = chemical[0]['cas']
    prefix = chemical[0].get('prefix','')
    name = chemical[0]['name']
    haz_substance = chemical[0]['haz_substance']
    dg_class_id = chemical[0].get('dg_class_id','')
    dg_class_2_id = chemical[0].get('dg_class_2_id','')
    dg_class_3_id = chemical[0].get('dg_class_3_id','')
    packing_group_id = chemical[0].get('packing_group_id','')
    un_number = chemical[0].get('un_number','')
    schedule_id = chemical[0].get('schedule_id','')
  elif response.status_code == 404:
    click.echo("Looks like we don't have any of that. We'll need some more information")
    prefix = click.prompt('What is the prefix of the chemical (if applicable)', default='')
    name = click.prompt('What is the name of the chemical?')
    haz_substance = click.prompt('Is this chemical a hazardous substance? (y/n)')
    dg_class = click.prompt('What is the dangerous goods class of the chemical? Subclasses can be indicated after a comma e.g 3, 6.1', default='').split(', ') + ['','','']
    while any(dg_class_element not in dg for dg_class_element in dg_class):
      dg_class = click.prompt("I am old and hard of hearing. Try entering that again").split(', ') + ['','','']
    packing_group = click.prompt('What is the packing group number of the chemical? (I, II, III)', default='')
    while packing_group not in pg:
      packing_group = click.prompt("I am old and hard of hearing. Try entering that again")
    un_number = click.prompt('What is the UN number of the chemical?', default='')
    schedule = click.prompt('What is the poisons schedule of this chemical?', default='')
    while schedule not in sched:
      schedule = click.prompt("I am old and hard of hearing. Try entering that again")

    dg_class_id = dg[dg_class[0]]
    dg_class_2_id = dg[dg_class[1]]
    dg_class_3_id = dg[dg_class[2]]
    packing_group_id = pg[packing_group]
    schedule_id = sched[schedule]
  else:
    click.echo('There seems to be a problem talking to the database...')
    return 0

  container_size_string = click.prompt('What is the container size?')
  location = click.prompt('Where will this chemical be stored?')
  while location not in loc:
    location = click.prompt("I am old and hard of hearing. Try entering that again")
  supplier = click.prompt('Who is the supplier of this chemical?')
  serial_number = click.prompt('The serial number for this container is', default = str(uuid.uuid1().int)[:12])

  container_size = str(ureg(container_size_string).magnitude)
  size_unit = str(ureg(container_size_string).units)
  supplier_id = '0'
  location_id = loc[location]

  if click.confirm('Create this chemical?'):
    url = "http://" + hostport + "/api/container/create?cas=" + str(cas) + "&prefix=" + str(prefix) + "&name=" + str(name) + "&dg_class_id=" + str(dg_class_id) + "&dg_class_2_id=" + str(dg_class_2_id) + "dg_class_3_id=" + str(dg_class_3_id) + "&schedule_id=" + str(schedule_id) + "packing_group_id=" + str(packing_group_id) + "&un_number=" + str(un_number) + "&haz_substance=" + str(haz_substance) + "&serial_number=" + str(serial_number) + "&container_size=" + str(container_size) + "&size_unit=" + str(size_unit) + "&supplier_id=" + str(supplier_id) + "&location_id=" + str(location_id) + "&location=" + str(location) + "&supplier=" + str(supplier)
    requests.get(url)

    fulltext_name = prefix + name

    labels = [createLabel(serial_number,fulltext_name,location)]
    printLabel(labels)
    click.clear()

  pass

def removeChemical():
  click.clear()
  serial_number = click.prompt('Please enter the serial number of the chemical to be deleted')
  requests.get('http://' + hostport + '/api/container/delete/' + serial_number)
  click.echo("Chemical deleted!")
  time.sleep(1)
  pass

def updateLocation():
  click.clear()
  serial_number = click.prompt('Please enter the serial number of the chemical to be updated')
  location = click.prompt('Please enter the new location')
  try:
    location_id = loc[location]
    requests.get('http://' + hostport + '/api/container/update/' + serial_number + '?location_id=' + location_id + '&temp=false')
    click.echo("Location updated!")

    response = requests.get('http://' + hostport + '/api/container/' + serial_number).json()

    fulltext_name = response[0]['chemical']['prefix'] + response[0]['chemical']['name']
    location = ' '.join([str(response[0]['container_location'][-1].get('location', {}).get('parent', {}).get('name', '')), str(response[0]['container_location'][-1].get('location', {}).get('name', ''))])
    labels = [createLabel(serial_number,fulltext_name,location)]
    #labels[0].show()
    printLabel(labels)
  except:
    click.echo("There doesn't seem to be a location with that name.")
  time.sleep(1)
  pass

def reprintLabel():
  click.clear()
  serial_number = click.prompt('Enter the serial number of the chemical you wish to reprint the label for')

  response = requests.get('http://' + hostport + '/api/container/' + serial_number).json()

  fulltext_name = response[0]['chemical']['prefix'] + response[0]['chemical']['name']
  location = ' '.join([str(response[0]['container_location'][-1].get('location', {}).get('parent', {}).get('name', '')), str(response[0]['container_location'][-1].get('location', {}).get('name', ''))])
  labels = [createLabel(serial_number,fulltext_name,location)]

  #labels[0].show()
  printLabel(labels)
  pass

def reprintLabelByLoc():
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
    click.echo("I didn't recognise that location")

def stocktake():
  click.clear()
  click.echo("Stocktake mode allows you to specify a location, then scan the chemicals in that location. All chemicals that were previously in that location will be marked as lost.")
  location = click.prompt('Please enter the location to stocktake')
  if location in loc:
    location_id = loc[location]

    response = requests.get('http://' + hostport + '/api/container/location_id/' + location_id).json()

    for row in response:
      requests.get('http://' + hostport + '/api/container/update/' + row['serial_number'] + '?location_id=&temp=false')

    serial_number = ''
    while serial_number != 'quit':
      serial_number = click.prompt("Enter serial number ('quit' to exit stocktake mode)")
      requests.get('http://' + hostport + '/api/container/update/' + serial_number + '?location_id=' + location_id + '&temp=false')
    click.echo("Quitting stocktake mode...")
    time.sleep(1)

    response = requests.get('http://' + hostport + '/api/container/location_id/0').json()
    t = PrettyTable()
    t.field_names = ["Name"]
    for row in response:
      t.add_row([
      row['chemical']['prefix'] + row['chemical']['name'][0:45]
      ])
    click.echo(t)
    if click.confirm("These chemicals are lost. Delete them?"):
      for row in response:
        requests.get('http://' + hostport + '/api/container/delete/' + row['serial_number'])
  else:
    click.echo("There doesn't seem to be a location with that name.")
    time.sleep(1)
    pass
  click.clear()
  pass

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
        click.echo('CTRL + N: Create new chemical, CTRL + R: Remove a chemical, CTRL + U: Update location, CTRL + P: Reprint label, CTRL + L: Reprint labels for location, CTRL + S: Stocktake')
      elif c == '\x0e':
        createChemical()
      elif c == '\x12':
        removeChemical()
      elif c == '\x15':
        updateLocation()
      elif c == '\x10':
        reprintLabel()
      elif c == '\x0c':
        reprintLabelByLoc()
      elif c == '\x13':
        stocktake()
      elif c in ['\x1b[A', '\x1b[B', '\x1b[C', '\x1b[D']:
        pass
      else:
        query = query + c

      click.echo('👨🏻‍🔬 *sighhh* I am CoLIn, what chemical do you want? Enter a name, CAS or container number. CTRL + H for help.')
      click.echo('\nSearch: ' + query)

      if len(query) > 5 and query[-1:] != '\r':
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
#        try:
          response = requests.get('http://' + hostport + '/api/container/search/' + query[:-1] + '?live=false').json()
          t = PrettyTable()
          t.field_names = ["Serial number", "CAS number", "Name", "DG Class", "Size", "Location", "Supplier"]
          for row in response:
            parent_loc = str(row['container_location'][-1].get('location', {}).get('parent', {}).get('name', ''))
            cont_loc = str(row['container_location'][-1].get('location', {}).get('name', ''))
            location = ' '.join([parent_loc, cont_loc])
            t.add_row([
              row['serial_number'],
              row['chemical']['cas'],
              row['chemical']['prefix'] + row['chemical']['name'][0:45],
              row['chemical'].get('dg_class', {}).get('description', ''),
              #'{:~}'.format(ureg(str(row['container_size']) + ' ' + str(row['size_unit'])).to_compact()),
              ureg(str(row['container_size']) + ' ' + str(row['size_unit'])),
              location,
              row['supplier']['name']
            ])
          click.echo(t)
          click.pause()
#        except:
#          pass

if __name__ == '__main__':
    colin()
