#!/bin/bash

openssl s_client -connect $1:443 -CAfile ./certs.pem << EOF
EOF
