#!/bin/mksh
#-
# Copyright © 2016
#	mirabilos <m@mirbsd.org>
#	Dominik „Natureshadow“ George <nik@naturalnet.de>
#
# Provided that these terms and disclaimer and all copyright notices
# are retained or reproduced in an accompanying document, permission
# is granted to deal in this work without restriction, including un‐
# limited rights to use, publicly perform, distribute, sell, modify,
# merge, give away, or sublicence.
#
# This work is provided “AS IS” and WITHOUT WARRANTY of any kind, to
# the utmost extent permitted by applicable law, neither express nor
# implied; without malicious intent or gross negligence. In no event
# may a licensor, author or contributor be held liable for indirect,
# direct, other damage, loss, or other issues arising in any way out
# of dealing in the work, even if advised of the possibility of such
# damage or existence of a defect, except proven that it results out
# of said person’s immediate fault when using the work as intended.
#-
# Receiver for a GitHub push webhook to trigger build and deployment.
#
# Should be placed somewhere where it is executable as CGI, e.g.
# /usr/lib/cgi-bin.

function die {
	print Status: $1
	shift

	print "Content-Type: text/plain"
	print
	print -r -- "$@"

	exit 1
}

# Verify request method
[[ ${REQUEST_METHOD} = POST ]] || die 405 "GitHub webhooks are always POSTed."

# Store body of request
body=$(cat; echo x)
body=${body%x}

# Calculate expected HMAC of request body
hmac=$(print -nr -- "${body}" | openssl sha1 -hmac "$(</etc/veripeditus-github-secret)")
hmac=${hmac##* }

# Compare HMACs and exit if authentication fails
if [[ ${HTTP_X_HUB_SIGNATURE} != "sha1=${hmac}" ]]; then
	# Prevent timing attacks
	sleep 0.$RANDOM

	die 400 "HMAC authentication failed."
fi

# FIXME add build magic

print "Content-Type: text/plain"
print
print "OK"

exit 0
