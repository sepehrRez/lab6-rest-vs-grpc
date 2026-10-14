## Results
All numbers are ms per operation. PING is the average round-trip time.

| Method          | Local | Same-Zone | Different Region |
|-----------------|------:|----------:|-----------------:|
| REST add        |  2.91 |      3.57 |           352.70 |
| gRPC add        |  0.72 |      1.18 |           185.02 |
| REST rawimg     |  5.57 |      7.50 |          1575.31 |
| gRPC rawimg     | 11.07 |     13.33 |           367.79 |
| REST dotproduct |  3.36 |      4.28 |           446.63 |
| gRPC dotproduct |  0.81 |      1.39 |           296.02 |
| REST jsonimg    | 25.30 |     31.11 |          1832.74 |
| gRPC jsonimg    | 22.21 |     26.53 |           222.51 |
| PING            | 0.053 |     0.443 |           177.82 |

## Observations
Locally and in the same zone the network is basically free (ping under 0.5 ms), so what we're
really measuring is software overhead. gRPC was around 3-4x faster for the small calls (add,
dotproduct) since it sends a small binary message on a connection that's already open, while
REST has to open a new TCP connection and go through HTTP + JSON + Flask every time.

Going to Frankfurt, network latency takes over. Ping was ~178 ms. REST add took ~353 ms, which
is about 2 round trips: one to set up the TCP connection and one for the actual request. gRPC
add took ~185 ms, about 1 round trip, because it keeps one connection open for all the calls.

The images show the biggest gap. REST needed roughly 9-10 round trips per image, because every
new connection starts with TCP slow start and has to ramp up before it can send 1.6 MB fast.
gRPC reuses a connection that's already warmed up, so it was about 4x faster for rawimg and
8x faster for jsonimg.

A few other things I noticed:
- The connection reuse matters way more than binary vs JSON. That's where most of gRPC's win
  comes from across regions.
- gRPC was actually slower than REST for rawimg locally and in the same zone (about 2x). My
  guess is sending a 1.6 MB message through gRPC costs more CPU on a small 2-vCPU VM.
- jsonimg is slower than rawimg for REST because base64 makes the image ~33% bigger. For gRPC
  cross-region I got jsonimg faster than rawimg, which doesn't make much sense, so that's
  probably network noise between runs.