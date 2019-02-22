from django.core.management.base import BaseCommand, CommandError
from restapi.models import Country

import os
"""
This class adds country codes to database
It uses ISO 3166-1 format https://en.wikipedia.org/wiki/ISO_3166-1
"""
class Command(BaseCommand):
    help = 'Add country codes to database'

    def add_arguments(self, parser):
        parser.add_argument('file', nargs=1, type=str, help='File containing country codes in CSV format')

    def handle(self, *args, **options):
        try:
            country_file = open(options['file'][0], 'r')
        except IOError as err:
            raise CommandError(err.strerror + ' ' + options['file'][0])
        
        with country_file:
            discarded = 0
            new = 0
            for line in country_file:
                elements = line.split(',')
                try:
                    Country.objects.create(name=elements[0], code2=elements[1], code3=elements[2], number=elements[3])
                    new += 1
                except:
                    discarded += 1
                    continue
        self.stdout.write(self.style.SUCCESS('{added} element(s) have been added and {discarded} element(s) have been discarded'.format(added=new, discarded=discarded)))
        

                