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

import route_guide_pb2
import route_guide_pb2_grpc
import route_guide_resources

from concurrent import futures
import logging
import math
import time

import grpc


class RouteGuideServicer(route_guide_pb2_grpc.RouteGuideServicer):
    def __init__(self):
        self.db = route_guide_resources.read_route_guide_database()

    def get_feature(self, point):
        for feature in self.db:
            if feature.location == point:
                return feature
        return None

    def get_distance(self, start, end):
        coord_factor = 10000000.0
        lat_1 = start.latitude / coord_factor
        lat_2 = end.latitude / coord_factor
        lon_1 = start.longitude / coord_factor
        lon_2 = end.longitude / coord_factor

        lat_rad_1 = math.radians(lat_1)
        lat_rad_2 = math.radians(lat_2)
        delta_lat_rad = math.radians(lat_2 - lat_1)
        delta_lon_rad = math.radians(lon_2 - lon_1)

        # see http://mathforum.org/library/drmath/view/51879.html
        a = (pow(math.sin(delta_lat_rad / 2), 2)
             + (math.cos(lat_rad_1) * math.cos(lat_rad_2)
             * pow(math.sin(delta_lon_rad / 2), 2)))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        R = 6371000
        return R * c

    def GetFeature(self, request, context):
        feature = self.get_feature(request)
        if (feature is None):
            return route_guide_pb2.Feature(name='', location=request)
        return feature

    def ListFeatures(self, request, context):
        left = min(request.lo.longitude, request.hi.longitude)
        right = max(request.lo.longitude, request.hi.longitude)
        top = max(request.lo.latitude, request.hi.latitude)
        bottom = min(request.lo.latitude, request.hi.latitude)
        for feature in self.db:
            loc = feature.location
            if (loc.longitude >= left and loc.longitude <= right
                    and loc.latitude >= bottom and loc.latitude <= top):
                yield feature

    def RecordRoute(self, request_iterator, context):
        point_count = 0
        feature_count = 0
        distance = 0.0
        prev_point = None

        start_time = time.time()
        for point in request_iterator:
            point_count += 1
            if self.get_feature(point):
                feature_count += 1
            if prev_point:
                distance += self.get_distance(prev_point, point)
            prev_point = point

        elapsed_time = time.time() - start_time
        return route_guide_pb2.RouteSummary(point_count=point_count,
                                            feature_count=feature_count,
                                            distance=int(distance),
                                            elapsed_time=int(elapsed_time))

    def RouteChat(self, request_iterator, context):
        prev_notes = []
        for new_note in request_iterator:
            for prev_note in prev_notes:
                if prev_note.location == new_note.location:
                    yield prev_note
            prev_notes.append(new_note)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    route_guide_pb2_grpc.add_RouteGuideServicer_to_server(
        RouteGuideServicer(), server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
