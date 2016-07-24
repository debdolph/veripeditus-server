#!/bin/mksh

angular-gettext-cli --files "./*.+(js|html)" --dest ./i18n/veripeditus-web.pot --marker-name i18n
