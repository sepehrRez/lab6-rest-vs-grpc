#!/usr/bin/env python3
"""gRPC client for measuring server operations (mirrors rest-client.py)."""

from __future__ import print_function

import argparse
import base64
import random
import time

import grpc

import lab6_pb2
import lab6_pb2_grpc


def doAdd(stub, debug=False):
    response = stub.Add(lab6_pb2.AddMsg(a=5, b=10))
    if debug:
        print("Response is", response)


def doRawImage(stub, debug=False):
    img = open('Flatirons_Winter_Sunrise_edit_2.jpg', 'rb').read()
    response = stub.RawImage(lab6_pb2.RawImageMsg(img=img))
    if debug:
        print("Response is", response)


def doDotProduct(stub, debug=False):
    a = [random.random() for _ in range(100)]
    b = [random.random() for _ in range(100)]
    response = stub.DotProduct(lab6_pb2.DotProductMsg(a=a, b=b))
    if debug:
        print("Response is", response)


def doJsonImage(stub, debug=False):
    img = open('Flatirons_Winter_Sunrise_edit_2.jpg', 'rb').read()
    img_b64 = base64.b64encode(img).decode('utf-8')
    response = stub.JsonImage(lab6_pb2.JsonImageMsg(img=img_b64))
    if debug:
        print("Response is", response)


# ---------------------------------------------------------
# Parse command-line arguments
# ---------------------------------------------------------

parser = argparse.ArgumentParser(
    description='gRPC client for measuring server operations'
)

parser.add_argument(
    'host',
    help='IP address or hostname of the gRPC server'
)

parser.add_argument(
    'cmd',
    choices=['add', 'rawImage', 'dotProduct', 'jsonImage'],
    help='Operation to perform'
)

parser.add_argument(
    'reps',
    type=int,
    help='Number of repetitions for measurement'
)

parser.add_argument(
    '-p', '--port',
    type=int,
    default=50051,
    help='Server port (default: 50051)'
)

parser.add_argument(
    '-d', '--debug',
    action='store_true',
    help='Print the response from the server'
)

args = parser.parse_args()

# ---------------------------------------------------------
# Build channel/stub (single persistent connection for all reps)
# ---------------------------------------------------------

addr = f"{args.host}:{args.port}"

print(f"Running {args.reps} reps against {addr}")

channel = grpc.insecure_channel(addr)
stub = lab6_pb2_grpc.Lab6Stub(channel)

# ---------------------------------------------------------
# Perform requested operation
# ---------------------------------------------------------

ops = {
    'rawImage': doRawImage,
    'add': doAdd,
    'jsonImage': doJsonImage,
    'dotProduct': doDotProduct,
}

func = ops[args.cmd]

# Warm up (establish connection, hide handshake cost from measurement)
func(stub, debug=False)

start = time.perf_counter()

for _ in range(args.reps):
    func(stub, debug=args.debug)

delta = ((time.perf_counter() - start) / args.reps) * 1000
print("Took", delta, "ms per operation")