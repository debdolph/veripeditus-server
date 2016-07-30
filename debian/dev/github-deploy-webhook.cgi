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
# /usr/lib/cgi-bin. Upon receiving a push event for a branch listed
# in $BRANCHES, it writes a signal file to $STATEDIR for the build
# script to pick up.
#
# Dependencies:
#   openssl, jq

BRANCHES="master"
SECRET=$(</etc/veripeditus-github-secret)
STATEDIR=/var/spool/veripeditus/build/signals

function ret {
	local status=$1; shift

	print Status: ${status}
	print "Content-Type: text/plain"
	print
	print -r -- "$@"

	if [[ ${status} = 2?? ]]; then
		exit 0
	else
		exit 1
	fi
}

# Verify request method
[[ ${REQUEST_METHOD} = POST ]] || ret 405 "GitHub webhooks are always POSTed."

# Store body of request
body=$(cat; echo x)
body=${body%x}

# Calculate expected HMAC of request body
hmac=$(print -nr -- "${body}" | openssl sha1 -hmac "${SECRET}")
hmac=${hmac##* }

# Compare HMACs and exit if authentication fails
if [[ ${HTTP_X_HUB_SIGNATURE} != "sha1=${hmac}" ]]; then
	# Prevent timing attacks
	sleep 0.$RANDOM

	ret 400 "HMAC authentication failed."
fi

# Handle event types
case ${HTTP_X_GITHUB_EVENT} in
(push)
	# Determine ref that was pushed
	ref=$(print -nr -- "${body}" | jq -r .ref)
	# Is it a branch head?
	if [[ ${ref} = refs/heads/* ]]; then
		# Get branch name
		branch=${ref#refs/heads/}

		# Do we trigger on that branch?
		if [[ " ${BRANCHES} " = *" ${branch} "* ]]; then
			# Determine the exact commit to build
			head=$(print -nr -- "${body}" | jq -r .head)

			# Touch a state file to signal a new build request
			print -nr -- "${head}" >"${STATEDIR}/${branch}"

			# Done!
			ret 202 "Build for branch ${head} (${branch}) triggered."
		else
			# Tell we are not interested, but happy ☺
			ret 200 "Pushes for branch ${branch} are ignored."
		fi
	fi
	;;
(*)
	# Not interested
	ret 200 "Not interested in this event."
	;;
esac

# If we got here, something is horribly wrong…
ret 500 "Oops, you found a non-existing code path ☹!"
