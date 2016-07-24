#!/bin/mksh

angular-gettext-cli --compile --files 'i18n/*.po' --dest i18n/i18n.js --format javascript --module Veripeditus
