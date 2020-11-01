import logging
import os
import aiohttp
from aiohttp import web, MultipartWriter

logging.basicConfig()
log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
logger = logging.getLogger("server")
log_level = getattr(logging, log_level)
logger.setLevel(log_level)


class StreamHandler:

    def __init__(self, cam):
        self._cam = cam

    async def __call__(self, request):
        my_boundary = 'image-boundary'
        response = web.StreamResponse(
            status=200,
            reason='OK',
            headers={
                'Content-Type': 'multipart/x-mixed-replace;boundary={}'.format(my_boundary)
            }
        )
        await response.prepare(request)
        while True:
            frame = await self._cam.get_frame()
            with MultipartWriter('image/jpeg', boundary=my_boundary) as mpwriter:
                mpwriter.append(frame, {
                    'Content-Type': 'image/jpeg'
                })
                try:
                    await mpwriter.write(response, close_boundary=False)
                except ConnectionResetError :
                    logger.warning("Client connection closed")
                    break
            await response.write(b"\r\n")


class MjpegServer:

    def __init__(self, host='0.0.0.0', port='8080'):
        self._port = port
        self._host = host
        self._app = web.Application()
        self._cam_routes = []

    async def root_handler(self, request):
        # TO-DO : load page with links
        text = 'Available streams:\n\n'
        for route in self._cam_routes:
            text += f"{route} \n"
        return aiohttp.web.Response(text=text)

    def add_stream(self, route, cam):
        route = f"/{route}"
        self._cam_routes.append(route)
        assert hasattr(cam, 'get_frame'), "arg 'cam' should have a 'get_frame' method"
        self._app.router.add_route("GET", f"{route}", StreamHandler(cam))

    def start(self):
        self._app.router.add_route("GET", "/", self.root_handler)
        web.run_app(self._app, host=self._host, port=self._port)

    def stop(self):
        '''
        dummy method
        actions to be take on closing can be added here
        '''
        pass
