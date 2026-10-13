#!/usr/bin/env python3
"""gRPC server implementing the same four services as the REST API."""

import argparse
import base64
import io
from concurrent import futures

import grpc
from PIL import Image

import lab6_pb2
import lab6_pb2_grpc


class Lab6Servicer(lab6_pb2_grpc.Lab6Servicer):

    def Add(self, request, context):
        return lab6_pb2.AddReply(sum=request.a + request.b)

    def RawImage(self, request, context):
        try:
            ioBuffer = io.BytesIO(request.img)
            img = Image.open(ioBuffer)
            width, height = img.size[0], img.size[1]
        except Exception:
            width, height = 0, 0
        return lab6_pb2.ImageReply(width=width, height=height)

    def DotProduct(self, request, context):
        result = sum(x * y for x, y in zip(request.a, request.b))
        return lab6_pb2.DotProductReply(dotproduct=result)

    def JsonImage(self, request, context):
        try:
            img_bytes = base64.b64decode(request.img)
            ioBuffer = io.BytesIO(img_bytes)
            img = Image.open(ioBuffer)
            width, height = img.size[0], img.size[1]
        except Exception:
            width, height = 0, 0
        return lab6_pb2.ImageReply(width=width, height=height)


def serve(port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    lab6_pb2_grpc.add_Lab6Servicer_to_server(Lab6Servicer(), server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    print(f"gRPC server listening on port {port}")
    server.wait_for_termination()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='gRPC server')
    parser.add_argument('-p', '--port', type=int, default=50051,
                        help='Port on which to run the server (default: 50051)')
    args = parser.parse_args()
    serve(args.port)