#!/bin/mksh

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
