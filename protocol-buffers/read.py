#!/usr/bin/env python

from addressbook_pb2 import Person, AddressBook
import sys

# Iterates though all people in the AddressBook and prints info about them.
def ListPeople(address_book):
  for person in address_book.people:
    print(f'Person ID: {person.id}')
    print(f'  Name: {person.name}')

    print(f'  E-mail address: {person.email}')

    for phone_number in person.phones:
      if phone_number.type == Person.PhoneType.MOBILE:
        print('  Mobile phone #: ', end='')
      elif phone_number.type == Person.PhoneType.HOME:
        print('  Home phone #: ', end='')
      elif phone_number.type == Person.PhoneType.WORK:
        print('  Work phone #: ', end='')
      print(phone_number.number)

# Main procedure:  Reads the entire address book from a file and prints all
#   the information inside.
if len(sys.argv) != 2:
  print(f'Usage: {sys.argv[0]} ADDRESS_BOOK_FILE')
  sys.exit(-1)

address_book = AddressBook()

# Read the existing address book.
f = open(sys.argv[1], 'rb')
address_book.ParseFromString(f.read())
f.close()

ListPeople(address_book)
