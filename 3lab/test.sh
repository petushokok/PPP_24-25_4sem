#!/bin/sh

curl -X POST http://localhost:8099/binary_image \
     -H "Content-Type: application/json" \
     --data @payload.json

