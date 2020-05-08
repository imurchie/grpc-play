# Copyright 2015 gRPC authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function

from route_guide_pb2 import RouteNote, Point, Rectangle
from route_guide_pb2_grpc import RouteGuideStub
import route_guide_resources

import random
import logging

from grpc import insecure_channel


def make_route_note(message, latitude, longitude):
    return RouteNote(
        message=message,
        location=Point(latitude=latitude, longitude=longitude)
    )


def guide_get_one_feature(stub, point):
    feature = stub.GetFeature(point)
    if not feature.location:
        print('Server returned incomplete feature')
        return

    if feature.name:
        print(f'Feature called {feature.name} at {feature.location}')
    else:
        print(f'Found not feature at {feature.location}')


def guide_get_feature(stub):
    guide_get_one_feature(
        stub,
        Point(latitude=409146138, longitude=746188906)
    )
    guide_get_one_feature(
        stub,
        Point(latitude=0, longitude=0)
    )


def guide_list_features(stub):
    rectangle = Rectangle(
        lo=Point(latitude=400000000, longitude=750000000),
        hi=Point(latitude=420000000, longitude=730000000)
    )
    print(f'Looking for features betwee 40, -75 and 42, -73')

    features = stub.ListFeatures(rectangle)
    for feature in features:
        print(f'Feature called {feature.name} at {feature.location}')


def generate_route(feature_list):
    for _ in range(0, 10):
        random_feature = feature_list[random.randint(0, len(feature_list) - 1)]
        print(f'Visiting point {random_feature.location}')
        yield random_feature.location


def guide_record_route(stub):
    feature_list = route_guide_resources.read_route_guide_database()

    route_iterator = generate_route(feature_list)
    route_summary = stub.RecordRoute(route_iterator)
    print(f'Finished trip with {route_summary.point_count} points')
    print(f'Passed {route_summary.feature_count} features')
    print(f'Travelled {route_summary.distance} meters')
    print(f'It took {route_summary.elapsed_time} seconds')


def generate_messages():
    messages = [
        make_route_note('First message', 0, 0),
        make_route_note('Second message', 0, 1),
        make_route_note('Third message', 1, 0),
        make_route_note('Fourth message', 0, 0),
        make_route_note('Fifth message', 1, 0),
    ]
    for message in messages:
        print(f'Sending {message.message} at {message.location}')
        yield message


def guide_route_chat(stub):
    responses = stub.RouteChat(generate_messages())
    for response in responses:
        print(f'Received message {response.message} at {response.location}')


def run():
    print('here')
    with insecure_channel('localhost:50051') as channel:
        stub = RouteGuideStub(channel)
        print('-------------- GetFeature --------------')
        guide_get_feature(stub)
        print('-------------- ListFeatures --------------')
        guide_list_features(stub)
        print('-------------- RecordRoute --------------')
        guide_record_route(stub)
        print('-------------- RouteChat --------------')
        guide_route_chat(stub)


if __name__ == '__main__':
    logging.basicConfig()
    run()
