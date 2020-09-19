#!/usr/bin/env python
# -*- coding: utf-8 -*-
#################################################################################
# Author      : site-module Software Pvt. Ltd. (<https://site-module.com/>)
# Copyright(c): 2015-Present site-module Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.site-module.com/license.html/>
#################################################################################

"""
    Oobapi is a library for Python to interact with the Opencart's Web Service API.

    Questions, comments? http://site-module.com/ticket/index.php
"""

__author__ = "dev@site-module.com"
__version__ = "0.1.0"

import urllib
import warnings
import requests
import json
from . import xml2dict
from . import dict2xml
from . import unicode_encode
import base64
# from cStringIO import StringIO
# from io import StringIO
# import unicode_encode



class OpencartWebService(object):
    """
        Interacts with the Opencart WebService API, use XML for messages
    """
    MIN_COMPATIBLE_VERSION = '2.1.0.1'
    MAX_COMPATIBLE_VERSION = '3.2.0.x'

    def __init__(self, debug=False, headers=None, client_args=None):
        """
        Create an instance of OpencartWebService.

        In your code, you can use :
        from oobapi import OpencartWebService, OpencartWebServiceError

        try:
            opencart = OpencartWebService.new('http://localhost:8080/api', 'BVWPFFYBT97WKM959D7AVVD0M4815Y1L')
        except OpencartWebServiceError, e:
            print str(e)
            ...

        @param api_url: Root URL for the shop
        @param api_key: Authentification key
        @param debug: Debug mode Activated (True) or deactivated (False)
        @param headers: Custom header, is a dict accepted by httplib2 as instance
        @param client_args: Dict of extra arguments for HTTP Client (httplib2) as instance {'timeout': 10.0}
        """
        # if client_args is None:
        #     client_args = {}
        # self._api_url = api_url

        # if not self._api_url.endswith('/'):
        #     self._api_url += '/'
        #
        # if not self._api_url.endswith('/api/'):
        #     self._api_url += 'api/'

        self.debug = debug

        self.headers = headers
        if self.headers is None:
            self.headers = {'User-agent': 'Opencartapi: Python Opencart Library'}

        self.client = requests.session()
        # self.client.auth=(api_key, '')


    def _execute(self, url, method, data=None, files=None, add_headers=None):
        # """
        # Execute a request on the Opencart Webservice
        #
        # @param url: full url to call
        # @param method: GET, POST, PUT, DELETE, HEAD
        # @param data: for PUT (edit) and POST (add) only, the xml sent to Opencart
        # @param files: should contain {'image': (img_filename, img_file)}
        # @param add_headers: additional headers merged on the instance's headers
        # @return: tuple with (status code, header, content) of the response
        # """
        # print self.client
        # print self.client.body
        # print self.client.content
        if add_headers is None: add_headers = {}

        # Don't print when method = POST, because it contains an encoded URL
        # The print for POST is in the method add_with_url()
        if self.debug and data and method != 'POST':
            try:
                xml = parseString(data)
                pretty_body = xml.toprettyxml(indent="  ")
            except:
                pretty_body = data
            print ("Execute url: %s / method: %s\nbody: %s" % (url, method, pretty_body))

        request_headers = self.headers.copy()
        request_headers.update(add_headers)
        if not files:
            r = self.client.request(method, unicode_encode.encode(url), data=data, headers=request_headers)
        else:
            r = self.client.request(method, url, files=files, headers = {'User-agent': 'Opencartapi: Python Opencart Library'})

        # if self.debug: # TODO better debug logs
            # print ("Response code: %s\nResponse headers:\n%s\n"
                #    % (r.status_code, r.headers))
            # if r.headers.get('content-type') and r.headers.get('content-type').startswith('image'):
                # print ("Response body: Image in binary format\n")
            # else:
                # print ("Response body:\n%s\n" % r.content)
        # self._check_status_code(r.status_code, r.content)
        print (r.content)
        print (r.text)
        # self._check_version(r.headers.get('psws-version'))

        return r




class OpencartWebServiceDict(OpencartWebService):
    """
    Interacts with the Opencart WebService API, use dict for messages
    """

    def get_session_key(self, api_url, params, debug=False, headers=None):
        # """
        # """
        self._api_url = api_url
        self.debug = debug
        self.headers = headers
        if self.headers is None:
            self.headers = {'User-agent': 'Opencartapi: Python Opencart Library'}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        r = self._execute(api_url, 'POST', data=params, add_headers=headers)
        # self.client = requests.Session()
        # self.client.auth=(params, '')
        # client = Session()
        # print client
        # req = Request('POST', api_url, data=params, headers={})
        # prepped = req.prepare()
        # resp = client.send(prepped,
        #     verify=False,
        # )
        return r
        # return resp

    def validate_session_key(self, api_url, params, debug=False, headers=None):
        # """
        # """
        self._api_url = api_url
        self.debug = debug
        self.headers = headers
        if self.headers is None:
            self.headers = {'User-agent': 'Opencartapi: Python Opencart Library'}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        r = self._execute(api_url, 'POST', data=params, add_headers=headers)
        # self.client = requests.Session()
        # self.client.auth=(params, '')
        # client = Session()
        # print client
        # req = Request('POST', api_url, data=params, headers={})
        # prepped = req.prepare()
        # resp = client.send(prepped,
        #     verify=False,
        # )
        return r
