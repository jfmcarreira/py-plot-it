#!/usr/bin/python3

import os

############################################################################################
# Auxiliary functions
############################################################################################
def filterResults( results, col, value):
  filtResults = []
  for line in results:
    if line[col - 1] == value:
      filtResults.append(line)
  return filtResults

def filterSeveralResults( results, col, values):
  filtResults = []
  for line in results:
    for v in values:
      if line[col - 1] == v:
        filtResults.append(line)
        break
  return filtResults

def findColumn( line, keyword):
  for i in range( len( line ) ):
    if line[i] == keyword:
      return i
  return -1

# Returns an array of [ detail, name ]
def resultsGetDetails( results, col):
  members = []
  for line in results:
    value = line[col - 1]
    if value not in members:
      members.append( value )

  outMembers = []
  for line in members:
    outMembers.append([line, line])
  return outMembers


# Find name in mappins
def findMap( mappings, config):
  name = config
  for line in mappings:
    if line[0] == config:
      name = line[1]
      return name
  return name

# Find name in mappins
def translateMappings( mappings, details):
  outDetails = []
  for line in details:
    outDetails.append( [line[0], findMap( mappings, line[0] )] )
  return outDetails

def readResults(fname):
  resultsTable = []
  if os.path.isfile(fname):
    print("Reading results!!")
    for line in open(fname).readlines():
      if not line.startswith("#"):
        resultsTable.append(line.split())
  return resultsTable

def readResultsHeader(fname):
  if os.path.isfile(fname):
    print("Finding header!!")
    for line in open(fname).readlines():
      if line.startswith("#"):
        return line[1:].split()

def replaceLabelChars(label):
  label = label.replace('_', '\\_')
  return label

def processLabel(label):
  if label != "":
    #label = label[:-3]
    label = replaceLabelChars( label )
  return label

def formatNumber(value):
  if isinstance(value, str):
    if value == "--":
      return value
    else:
      assert(0)
  value = float(value)
  return str("%.2f" % ( value ) )
