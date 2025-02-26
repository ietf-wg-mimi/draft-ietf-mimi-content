#!/bin/bash
set -e
b=$(basename "${1}" .edn)
node edn2cbor "${1}" "${b}.cbor.tmp"

if cmp "${b}.cbor" "${b}.cbor.tmp" ; then
    echo "OK: ${1} matches its CBOR counterpart"
    rm "${b}.cbor.tmp"
else
    echo "FAIL: ${1} does not match its CBOR counterpart"
fi