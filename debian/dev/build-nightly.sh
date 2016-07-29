#!/bin/mksh
# Inspired by MirOS: contrib/hosted/tg/deb/BuildDSC.sh,v 1.19 2016/02/23 18:05:35 tg Exp $
#-
# Copyright (c) 2010, 2011
#	Thorsten Glaser <t.glaser@tarent.de>
# Copyright © 2015, 2016
#	mirabilos <m@mirbsd.org>
# Copyright © 2016
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

# sanitise environment
unset LANGUAGE
export LC_ALL=C

# preload
sync
date >/dev/null

# Change to correct directory
cd "$(realpath "$(dirname "$0")/../../")"

# Sanity checks
# check for DEBEMAIL
if [[ $DEBEMAIL != +([A-Za-z])*' <'*'>' ]]; then
	print -u2 'Please set $DEBEMAIL to "First M. Last <email@domain.com>"'
	exit 1
fi
# check for unstaged changes in Git
if ! git diff-index --quiet HEAD --; then
	print -u2 'You have uncommited changes in your working copy.'
	print -u2 'Commit or stash them before building!'
	exit 1
fi

# Get information about tree to build
tree=${1:-master}
commit=$(git rev-parse --short "${tree}")

# Store current point in history to return to later
current=$(git rev-parse HEAD)

# Build date
stime_rfc=$(date +"%a, %d %b %Y %H:%M:%S %z")
stime_vsn=$(date -u +"%Y%m%d.%H%M%S")

# Construct version suffix
suf=git.${stime_vsn}-${commit}

# Get information from debian changelog
dch_source=$(dpkg-parsechangelog -n 1 -S source)
dch_ver=$(dpkg-parsechangelog -n 1 -S version)
dch_dist=$(dpkg-parsechangelog -n 1 -S distribution)

# Determine new version
if [[ ${dch_dist} = UNRELEASED ]]; then
	# we’re at “current” already, reduce
	version=${dch_ver}'~'${suf}
else
	# we’re at an uploaded version, raise
	version=${dch_ver}'+'${suf}
fi

# Try to create temporary file for new changelog
if ! dch_temp=$(mktemp "$(realpath ..)/${dch_source}.nightly-build.tmp.XXXXXXXXXX"); then
	print -u2 Could not create temporary file.
	exit 1
fi

# Copy changelog to temporary file
cat debian/changelog >"${dch_temp}"
touch -r debian/changelog "${dch_temp}"

# Create new changelog entry
print "${dch_source} (${version}) UNRELEASED; urgency=low\n\n  *" \
    "Automatically built snapshot (not backport) package.\n\n --" \
    "${DEBEMAIL}  ${stime_rfc}\n" >debian/changelog
cat "${dch_temp}" >>debian/changelog
touch -r "${dch_temp}" debian/changelog

# Produce temporary commit
git commit -a --author "${DEBEMAIL}" -m "Automatic commit before gbp run."

# Merge tree to be build into this branch
git merge --no-edit --squash --commit -q "${tree}"

# Fire!
gbp buildpackage \
    --git-debian-branch=debian \
    --git-upstream-tree="${tree}" \
    --git-force-create \
    -us -uc
rv=$?

# Reset to state before doing anything
git reset --hard "${current}"

# Clean up
rm -f "${dch_temp}"

# Exit with saved status from gbp
exit ${rv}
