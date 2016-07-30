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
# Dependencies:
#   mksh, git, apt

BRANCH=${1:-master}
STATEDIR=/var/spool/veripeditus/build/signals

# Get location of script
me=$(realpath "$0")

# Look for something to build
if [[ -f "${STATEDIR}/${BRANCH}" ]]; then
	# Look for lock file
	if [[ -e "${STATEDIR}/${BRANCH}.lock" ]]; then
		# Do nothing if locked
		exit 0
	else
		# Create lock file
		touch "${STATEDIR}/${BRANCH}.lock"
	fi
fi

# Create temporary directory to work with
if ! d=$(mktemp -d); then
	print -u2 "Could not create temporary directory."
	exit 1
fi
cd "${d}"

# Copy signal file here for later time reference
cp "${STATEDIR}/${BRANCH}" .
touch -r "${STATEDIR}/${BRANCH}" "${BRANCH}"

# Get hold of repo and switch to the Debian branch
git clone https://github.com/Veripeditus/veripeditus-server
cd veripeditus-server
git checkout debian

# Check whether currently running script is up-to-date
if ! cmp -s "${me}" debian/dev/deploy-nightly.sh; then
	# Overwrite currently running script and restart
	exec mksh -c "cat debian/dev/deploy-nightly.sh >${me@Q}; cd /; rm -rf ${d@Q}; rm -f ${STATEDIR@Q}/${BRANCH@Q}.lock; exec ${me@Q}"
fi

# Execute nightly build script
mksh debian/dev/build-nightly.sh "$(<"../${BRANCH}")"
rv=$?

if (( !rv )); then
	# Install newly created packages with APT
	apt install "${d}/"*.deb
	rv=$?

	if (( rv )); then
		print -u2 "Failed to install packages."
	fi
else
	print -u2 "Failed to build packages."
fi

# cleanup
# Check whether no new build was registered for the branch
if ! [[ "${STATEDIR}/${BRANCH}" -nt "../${BRANCH}" ]]; then
	# Remove build signal
	rm -f "${STATEDIR}/${BRANCH}"
fi
# Remove lock file
rm -f "${STATEDIR}/${BRANCH}.lock"
# Remove temporary build directory
cd /
rm -rf "${d}"

# Exit with last known rv, either from gbp or apt
exit ${rv}
