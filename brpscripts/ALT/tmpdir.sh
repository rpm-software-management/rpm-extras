#!/bin/sh

remove_tmpdir()
{
       rm -rf -- "$tmpdir"
       exit $1
}

trap 'exit 143' HUP INT QUIT PIPE TERM
tmpdir=$(mktemp -dt "${0##*/}.XXXXXXXX")
trap 'remove_tmpdir $?' EXIT
