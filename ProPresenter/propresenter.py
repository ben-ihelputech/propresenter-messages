#!/usr/bin/env python3

import requests
import yaml
import argparse
import validators
import json
import time
import os
import datetime

parser = argparse.ArgumentParser()

parser.add_argument("-e", "--endpoint", 
        help="Set the endpoint URI to the ProPresenter Computer Ex: http://localhost:1025",
        required=True)
parser.add_argument("--debug", help="Set debug output", action="store_true")
parser.add_argument("-p", "--presentation", help="Get the current presentation", action="store_true")
parser.add_argument("-s", "--slide-index", help="Get the current slide in the presentation", action="store_true")
parser.add_argument("--active-message", help="Get the current active message", action="store_true")
parser.add_argument("-k", "--active-kids-message", help="Get the current active kids message", action="store_true")
parser.add_argument("-v", "--verbose", help="More verbose output", action="store_true")
parser.add_argument("-w", "--watch", help="Continously monitor the presentation and slide", action="store_true")
parser.add_argument("--refresh-rate", help="Sets the refresh rate of the --watch flag. Default is 5 seconds", type=int, default=5)

args = parser.parse_args()

endpoint = args.endpoint

if args.debug:
  print(args)

def load_config(file):
  with open(file) as stream:
    try:
  #print(yaml.safe_load(stream))
      return yaml.safe_load(stream)
    except yaml.YAMLError as exc:
      print(exc)

def send_request(endpoint: str, path: str, method: str):
  valid_methods = ["get"]
  method = method.lower()
  if method not in valid_methods:
    raise ValueError("Invalid or unsupport request method:", method)
  
  uri = endpoint + path
  try:
    valid = validators.url(uri)
    if args.debug:
      print("URI is valid:", uri)
  except Exception as err:
    print("URI not valid:", err)
    raise
  
  try:
    r = getattr(requests, method)(uri)
  except HTTPError as http_err:
    print(f"HTTP error occurred: {http_err}")
  except Exception as err:
    print(f"Other error occurred: {err}")
  else:
    return r

def get_current_message():
  path = "/v1/messages"
  response = send_request(endpoint, path, "get")
  if args.debug:
    print(response.text)
  active_messages = json.loads(response.text)

message_uuid = "3C37D8EE-A68C-477D-9A03-EA3FE3780CB1"
def get_kids_message(message_uuid):
  path = "/v1/message/" + message_uuid
  response = send_request(endpoint, path, "get")
  if args.debug:
    print(response.text)
  active_kids_message = json.loads(response.text)
  if args.verbose:
    print("Kids Tag ID:", active_kids_message["message"])
  return active_kids_message

def change_kids_message(message_uuid):
  path = "/v1/message/" + message_uuid
  response = send_request(endpoint, path, "put")
  if args.debug:
    print(response.text)
  active_kids_message = json.loads(response.text)
  if args.verbose:
    print("Kids Tag ID:", active_kids_message["message"])
  return active_kids_message

def get_current_presentation():
  path = "/v1/presentation/focused"
  response = send_request(endpoint, path, "get")
  if args.debug:
    print(response.text)
  presentation = json.loads(response.text)
  if args.verbose:
    print("Name:", presentation["name"]) 
    print("Presentation Index:", presentation["index"]) 
    print("UUID:", presentation["uuid"]) 
  return presentation

def get_current_slide():
  path = "/v1/presentation/slide_index"
  response = send_request(endpoint, path, "get")
  if args.debug:
    print(response.text)
  slide_index = json.loads(response.text)
  if args.verbose:
    print("Slide Index:", slide_index["presentation_index"]["index"]) 
  return slide_index

def watch_loop(rate):
  try:
    datetime.datetime(2009, 1, 6, 15, 8, 24, 78915)
    while True:
      if rate < 1:
        raise ValueError("Cannot specify refresh rate less than 1 second")
      p = get_current_presentation()
      s = get_current_slide()
      os.system('cls' if os.name == 'nt' else 'clear')
      now = datetime.datetime.now()
      print(now)
      print("Presentation Name:", p["name"])
      print("Presentation Index:", p["index"])
      print("Presentation ID:", p["uuid"])
      print("Slide Number:", s["presentation_index"]["index"]) 
      time.sleep(rate)
  except KeyboardInterrupt:
    print("Stopping watch loop")

if __name__ == "__main__":
  #print("Testing")
  if args.presentation:
    get_current_presentation()
  if args.slide_index:
    get_current_slide()
  if args.active_message:
    get_current_message()
  if args.active_kids_message:
    get_kids_message("3C37D8EE-A68C-477D-9A03-EA3FE3780CB1")
  if args.watch:
    watch_loop(args.refresh_rate)

